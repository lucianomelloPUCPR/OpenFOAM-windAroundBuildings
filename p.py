import os

# Directory containing STL files
stl_directory = 'constant/triSurface/' 

# Path to the output p file
output_file_path = '0/p'

# Normalize paths
stl_directory = os.path.normpath(stl_directory)
output_file_path = os.path.normpath(output_file_path)

# Find all STL files in the specified directory
stl_files = [f for f in os.listdir(stl_directory) if f.lower().endswith('.stl')]

# Prepare the refinement surfaces block
refinement_surfaces_block = ""
for stl_file in stl_files:
    base_name = os.path.splitext(stl_file)[0]
    refinement_surfaces_block += f'    {base_name}\n    {{\n        type            zeroGradient;\n    }}\n'

# Template for the p file content
p_content = f'''/*--------------------------------*- C++ -*----------------------------------*\\
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
    object      p;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

pOut            1e5;

dimensions      [1 -1 -2 0 0 0 0];

internalField   uniform $pOut;

boundaryField
{{
    "(inlet|floor)"
    {{
        type            zeroGradient;
    }}

    "(outlet|front|back|top)"
    {{
        type            totalPressure;
        p0              uniform $pOut;
        value           uniform $pOut;
    }}


{refinement_surfaces_block}

    #includeEtc "caseDicts/setConstraintTypes"
}}

// ************************************************************************* //
'''

# Write the generated content to the p file
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
with open(output_file_path, 'w') as output_file:
    output_file.write(p_content)

print(f"p boundary condition file has been generated successfully at {output_file_path}.")
