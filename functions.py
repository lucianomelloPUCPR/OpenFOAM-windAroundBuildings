import os
from stl import mesh
import numpy as np
import simu

# Paths
stl_directory= 'constant/triSurface/'
functions_file_path = 'system/functions'
vtk_output_folder = 'postProcessing/probeVTK'
csv_output_file = 'postProcessing/probeLocations.csv'

# Settings
projection_distance = simu.projectionDistance
interval = simu.interval

os.makedirs(os.path.dirname(functions_file_path), exist_ok=True)
os.makedirs(vtk_output_folder, exist_ok=True)
os.makedirs(os.path.dirname(csv_output_file), exist_ok=True)

stl_files = [f for f in os.listdir(stl_directory) if f.endswith('.stl')]

surface_names = []
csv_lines = ['x,y,z,surface']

def calculate_probe_positions(stl_file, projection_distance):
    full_path = os.path.join(stl_directory, stl_file)
    if any(key in stl_file.lower() for key in ['porta', 'janela']):
        return np.array([])
    try:
        tri_mesh = mesh.Mesh.from_file(full_path)
    except Exception as e:
        print(f"Error reading {stl_file}: {e}")
        return np.array([])

    probes = []
    for i in range(len(tri_mesh)):
        A, B, C = tri_mesh.v0[i], tri_mesh.v1[i], tri_mesh.v2[i]
        AB, AC = B - A, C - A
        normal = np.cross(AB, AC)
        norm = np.linalg.norm(normal)
        if norm < 1e-8:
            continue
        normal /= norm
        stl_normal = tri_mesh.normals[i]
        if np.dot(normal, stl_normal) < 0:
            normal *= -1
        barycenter = (A + B + C) / 3
        probe = barycenter + projection_distance * normal
        probes.append(probe)
    return np.array(probes)

# Header of functions file
functions_content = f'''/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website: https://openfoam.org
    \\  /    A nd           | Version: 12
     \\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    format      ascii;
    class       dictionary;
    object      functions;
}}

#includeFunc residuals

 yPlus
    {{
        type            yPlus;
        functionObjectLibs ("libfieldFunctionObjects.so");
        outputControl   timeStep; // or writeTime or timeStep as needed
        outputInterval  {interval};
    }}
'''

# Loop through STL surfaces
for stl_file in stl_files:
    surface_name = os.path.splitext(stl_file)[0]
    probe_positions = calculate_probe_positions(stl_file, projection_distance)

    if 'porta' not in stl_file.lower() and 'janela' not in stl_file.lower():
        surface_names.append(f'\t\t\t\t\t\t"{surface_name}"')

    if probe_positions.size == 0:
        continue

    functions_content += f'''
    sample_near_{surface_name}
    {{
        type            probes;
        functionObjectLibs ("libsampling.so");
        enabled         true;
        writeControl    timeStep;
        writeInterval   {interval};
        fields ( U T p );
        probeLocations
        (
'''
    vtk_points = []
    for probe in probe_positions:
        functions_content += f'            ({probe[0]:.6f} {probe[1]:.6f} {probe[2]:.6f})\n'
        csv_lines.append(f"{probe[0]:.6f},{probe[1]:.6f},{probe[2]:.6f},{surface_name}")
        vtk_points.append(probe)

    functions_content += '        );\n    }\n'

    # Write VTK for visualization
    vtk_path = os.path.join(vtk_output_folder, f'{surface_name}.vtk')
    with open(vtk_path, 'w') as vtk:
        vtk.write("# vtk DataFile Version 2.0\nProbe Points\nASCII\nDATASET POLYDATA\n")
        vtk.write(f"POINTS {len(vtk_points)} float\n")
        for pt in vtk_points:
            vtk.write(f"{pt[0]} {pt[1]} {pt[2]}\n")
        vtk.write(f"\nVERTICES {len(vtk_points)} {len(vtk_points)*2}\n")
        for i in range(len(vtk_points)):
            vtk.write(f"1 {i}\n")

# Add HTC block
functions_content += f'''
    htc_surfaces
    {{
        type        wallHeatTransferCoeff;
        libs        ("libfieldFunctionObjects.so");
        enabled     true;
        model       kappaEff;
        patches     (
{os.linesep.join(surface_names)}
        );
        rho         1.225;
        Cp          1005;
        Pr          0.707;
        Prt         0.09;  // <-- Reduced from 0.9 to 0.09 to multiply h by 10
        writeControl timeStep;
        writeInterval   {interval};
    }}
'''

# Add pressure coefficient block
functions_content += f'''
    pressure_coeff
    {{
        type            pressure;
        functionObjectLibs ("libfieldFunctionObjects.so");
        log             yes;
        writeControl    timeStep;
        writeInterval   {interval};
        enabled         yes;
        calcTotal       no;
        calcCoeff       yes;
        pRef            0;
        rhoInf          1.125;
        pInf            0;
        UInf            ({simu.velo[0]} {simu.velo[1]} {simu.velo[2]});
    }}

'''

# Save the functions dictionary
with open(functions_file_path, 'w') as f:
    f.write(functions_content)

# Save CSV with probe locations
with open(csv_output_file, 'w') as csv_file:
    csv_file.write('\n'.join(csv_lines))

print(f"Functions written to {functions_file_path}")
print(f"CSV of probe locations written to {csv_output_file}")
