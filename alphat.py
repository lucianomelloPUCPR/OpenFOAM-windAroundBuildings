import os

# Directory containing STL files
stl_directory = 'constant/triSurface/' 

# Path to the output k file
output_file_path = '0/alphat'

# Normalize paths
stl_directory = os.path.normpath(stl_directory)
output_file_path = os.path.normpath(output_file_path)

# Find all STL files in the specified directory
stl_files = [f for f in os.listdir(stl_directory) if f.lower().endswith('.stl')]

# Prepare the refinement surfaces block
refinement_surfaces_block = ""
for stl_file in stl_files:
    base_name = os.path.splitext(stl_file)[0]
    refinement_surfaces_block += f'    {base_name}\n    {{\n        type            compressible::alphatWallFunction;\n        value           uniform 0;\n    }}\n'

# Template for the k file content
alphat_content = f'''/*--------------------------------*- C++ -*----------------------------------*\\
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
    object      alphat;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [1 -1 -1 0 0 0 0];

internalField   uniform 0;

boundaryField
{{
    inlet
    {{
        type            calculated;
        value           uniform 0;
    }}

    outlet
    {{
        type            calculated;
        value           uniform 0;
    }}
    
    front
    {{
        type            calculated;
        value           uniform 0;
    }}
    
    back
    {{
        type            calculated;
        value           uniform 0;
    }}
    
    top
    {{
        type            calculated;
        value           uniform 0;
    }}
    
    floor
    {{
        type            compressible::alphatWallFunction;
        value           uniform 0;
    }}

{refinement_surfaces_block}

    #includeEtc "caseDicts/setConstraintTypes"
}}

// ************************************************************************* //
'''

# Write the generated content to the k file
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
with open(output_file_path, 'w') as output_file:
    output_file.write(alphat_content)

print(f"k boundary condition file has been generated successfully at {output_file_path}.")
