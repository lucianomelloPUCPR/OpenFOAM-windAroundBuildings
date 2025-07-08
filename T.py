# Surface area calculated for heat flux boundary condition

import warnings
# Suppress the FutureWarning from numpy
warnings.filterwarnings("ignore", category=FutureWarning)

import os
from stl import mesh  # Import numpy-stl for STL file handling
import numpy as np
import simu

# Directory containing STL files
stl_directory = 'constant/triSurface/' 

# Path to the output T file
output_file_path = '0/T'

# Demand power for heating from Domus
power_W = 3069.0

# Area of Zone - get from Domus
patch_area = 25.0

# Normalize paths
stl_directory = os.path.normpath(stl_directory)
output_file_path = os.path.normpath(output_file_path)


# Weather file temperature
weather_file_temperature = simu.T

# Function to calculate the area of a triangle
def calculate_triangle_area(v0, v1, v2):
    # Use the cross product to get the area of the triangle
    return 0.5 * np.linalg.norm(np.cross(v1 - v0, v2 - v0))

# Function to calculate the total surface area of the mesh
def calculate_surface_area(stl_path):
    try:
        stl_mesh = mesh.Mesh.from_file(stl_path)
        total_area = 0.0
        for i in range(len(stl_mesh)):
            v0, v1, v2 = stl_mesh.vectors[i]  # Get the vertices of each triangle
            total_area += calculate_triangle_area(v0, v1, v2)
        return total_area
    except Exception as e:
        print(f"Error loading STL file {stl_path}: {e}")
        return None

# Prepare the refinement surfaces block
surfaces_block = ""

# Find all STL files in the specified directory
stl_files = [f for f in os.listdir(stl_directory) if f.lower().endswith('.stl')]

for stl_file in stl_files:
    base_name = os.path.splitext(stl_file)[0]  # Get the base name without extension
    
    if "Ar_Condicionado" in base_name:  # Check if this surface is in the list 
        
        if patch_area is None or patch_area == 0:
            raise ValueError(f"Patch area for {base_name} is zero or invalid, check the STL file.")
        
        # Calculate heat flux (W/m²) - Under watch
        heat_flux = max(round(float(power_W / patch_area), 2), 0.01)

        # Debugging: Print the calculated heat flux and area
        #print(f"Calculated area for {base_name}: {patch_area:.2f} m²")
        #print(f"Calculated heat_flux for {base_name}: {heat_flux} W/m²")

        # Add the formatted heat flux to the surfaces block
        surfaces_block += (
            f'  {base_name}\n'
            f'  {{\n'
            f'      type            fixedGradient;\n'
            f'      gradient        uniform {heat_flux};\n'
            f'      value           uniform 300.0;\n'
            f'  }}\n\n'
        )      
    else:
        surfaces_block += (
            f'  {base_name}\n'
            f'  {{\n'
            f'      type            fixedValue;\n'
            f'      value           uniform 292.15;\n'
            f'  }}\n\n'
        )

# Template for the T file content

T_content = f'''/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  12
     \\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    format      ascii;
    class       volScalarField;
    object      T;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 1 0 0 0];

internalField   uniform 290;

boundaryField
{{
    inlet
    {{
        type            fixedValue;
        value           uniform {weather_file_temperature};
    }}

    "(outlet|front|back|top)"
    {{
        type            zeroGradient;
    }}

    floor
    {{
        type            fixedValue;
        value           uniform 290.0;
    }}

{surfaces_block}

    #includeEtc "caseDicts/setConstraintTypes"
}}

// ************************************************************************* //
'''

# Write the generated content to the T file
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
with open(output_file_path, 'w') as output_file:
    output_file.write(T_content)

print(f"T boundary condition file has been generated successfully at {output_file_path}.")
