import os

# === Paths ===
stl_directory = 'constant/triSurface/'
output_file_path = '0/nut'

# Normalize paths
stl_directory = os.path.normpath(stl_directory)
output_file_path = os.path.normpath(output_file_path)

# Find all STL files in the specified directory
stl_files = [f for f in os.listdir(stl_directory) if f.lower().endswith('.stl')]

# Create nut wall function entries for STL surfaces
surfaces_block = ""
for stl_file in stl_files:
    base_name = os.path.splitext(stl_file)[0]
    surfaces_block += (
        f'    {base_name}\n'
        f'    {{\n'
        f'        type            nutkWallFunction;\n'
        f'        value           uniform 0;\n'
        f'    }}\n\n'
    )

# Build the full nut field file content
nut_content = f'''/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\\\    /   O peration     | Website:  https://openfoam.org
    \\\\  /    A nd           | Version:  12
     \\\\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    format      ascii;
    class       volScalarField;
    object      nut;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 0;

boundaryField
{{
    "(inlet|outlet|front|back|top)"
    {{
        type            calculated;
        value           uniform 0;
    }}

    floor
    {{
        type            nutkWallFunction;
        value           uniform 0;
    }}

{surfaces_block}    #includeEtc "caseDicts/setConstraintTypes"
}}

// ************************************************************************* //
'''

# Ensure output directory exists
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

# Write to nut file
with open(output_file_path, 'w') as output_file:
    output_file.write(nut_content)

print(f"Nut field successfully written to: {output_file_path}")
