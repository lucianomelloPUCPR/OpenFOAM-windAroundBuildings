import numpy as np
from stl import mesh
import os
import glob
import simu

# Directory containing STL files
stl_directory = 'constant/triSurface/' 

# Automatically find all STL files in the specified directory
stl_file_paths = glob.glob(os.path.join(stl_directory, "*.stl"))

# Normalize the paths for the operating system
stl_file_paths = [os.path.normpath(path) for path in stl_file_paths]

# Initialize min and max coordinates with extreme values
xmin, ymin, zmin = float('inf'), float('inf'), float('inf')
xmax, ymax, zmax = float('-inf'), float('-inf'), float('-inf')

xmin_geo, ymin_geo, zmin_geo = float('inf'), float('inf'), float('inf')
xmax_geo, ymax_geo, zmax_geo = float('-inf'), float('-inf'), float('-inf')

# Initialize an empty list to hold all meshes
all_meshes = []

# Iterate through all STL files to find the overall bounding box and combine them
for stl_file_path in stl_file_paths:
    your_mesh = mesh.Mesh.from_file(stl_file_path)
    all_meshes.append(your_mesh)

    coordinates = np.around(your_mesh.vectors.reshape(-1, 3), decimals=3).tolist()

    if coordinates:
        xmin_file, xmax_file = min(coord[0] for coord in coordinates), max(coord[0] for coord in coordinates)
        ymin_file, ymax_file = min(coord[1] for coord in coordinates), max(coord[1] for coord in coordinates)
        zmin_file, zmax_file = min(coord[2] for coord in coordinates), max(coord[2] for coord in coordinates)

        xmin = min(xmin, xmin_file)
        xmax = max(xmax, xmax_file)
        ymin = min(ymin, ymin_file)
        ymax = max(ymax, ymax_file)
        zmin = min(zmin, zmin_file)
        zmax = max(zmax, zmax_file)

        xmin_geo = min(xmin_geo, xmin_file)
        xmax_geo = max(xmax_geo, xmax_file)
        ymin_geo = min(ymin_geo, ymin_file)
        ymax_geo = max(ymax_geo, ymax_file)
        zmin_geo = min(zmin_geo, zmin_file)
        zmax_geo = max(zmax_geo, zmax_file)

# Padding value
paddingXY = simu.domainExpansionXY * zmax
paddingZ = simu.domainExpansionZ * zmax
padding_geo = simu.paddingDomain

# Apply padding to the overall bounding box
x_min = round(xmin - paddingXY, 2)
x_max = round(xmax + paddingXY, 2)

y_min = round(ymin - paddingXY, 2)
y_max = round(ymax + paddingXY, 2)

z_min = round(zmin, 3) if abs(zmin) >= 0.001 else 0.001
z_max = round(zmax + paddingZ, 2)

# Apply padding to the overall refinement box
x_min_geo = round(xmin_geo - padding_geo * abs(xmin_geo), 2)
x_max_geo = round(xmax_geo + padding_geo * abs(xmax_geo), 2)

y_min_geo = round(ymin_geo - padding_geo * abs(ymin_geo), 2)
y_max_geo = round(ymax_geo + padding_geo * abs(ymax_geo), 2)

z_min_geo = round(zmin_geo, 3) if abs(zmin_geo) >= 0.001 else 0.001
z_max_geo = round(zmax_geo + padding_geo * abs(zmax_geo), 2)


# blockMeshDict template
block_mesh_template = '''
/*--------------------------------*- C++ -*----------------------------------*
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  10
     \\/     M anipulation  |
*---------------------------------------------------------------------------*/
FoamFile
{{ 
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}} 
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
backgroundMesh
{{
    xMin    {};
    xMax    {};
    yMin    {};
    yMax    {};
    zMin    {};
    zMax    {};
    xCells  {};
    yCells  {};
    zCells  {};
}}
convertToMeters 1;
vertices
(
    ({} {} {})
    ({} {} {})
    ({} {} {})
    ({} {} {})
    ({} {} {})
    ({} {} {})
    ({} {} {})
    ({} {} {})
);
blocks
(
    hex (0 1 2 3 4 5 6 7)    
    fluid (
        $!backgroundMesh/xCells
        $!backgroundMesh/yCells
        $!backgroundMesh/zCells
    )    
    simpleGrading (1 1 1)
);

edges
(
);

defaultPatch
{{
    type wall;
}}

boundary
(
    top
    {{
        type patch;
        faces
        (
            (4 5 6 7)
        );
    }}
    floor
    {{
        type wall;
        faces
        (
            (0 3 2 1)
        );
    }}
    inlet
    {{
        type patch;
        faces
        (
            (0 4 7 3)
        );
    }}
    outlet
    {{
        type patch;
        faces
        (
            (1 2 6 5)
        );
    }}
    front
    {{
        type patch;
        faces
        (
            (0 1 5 4)
        );
    }}
    back
    {{
        type patch;
        faces
        (
            (3 7 6 2)
        );
    }}
);

mergePatchPairs
(
);
// ************************************************************************* //
'''

block_mesh_dict_content = block_mesh_template.format(
    x_min, x_max, y_min, y_max, z_min, z_max,
    simu.cells, simu.cells, simu.cells,
    x_min, y_min, z_min,
    x_max, y_min, z_min,
    x_max, y_max, z_min,
    x_min, y_max, z_min,
    x_min, y_min, z_max,
    x_max, y_min, z_max,
    x_max, y_max, z_max,
    x_min, y_max, z_max
)

output_file_path = 'system/blockMeshDict'
with open(output_file_path, 'w') as output_file:
    output_file.write(block_mesh_dict_content)

print("blockMeshDict file has been generated successfully.")
