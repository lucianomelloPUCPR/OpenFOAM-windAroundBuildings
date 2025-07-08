import os

# === CONFIGURATION ===
omega_value = 1.0  # [1/s] Set the inlet and wall omega value

# === Paths ===
stl_directory = 'constant/triSurface/'
output_file_path = '0/omega'

# Normalize paths
stl_directory = os.path.normpath(stl_directory)
output_file_path = os.path.normpath(output_file_path)

# List all STL files in the directory
stl_files = [f for f in os.listdir(stl_directory) if f.lower().endswith('.stl')]

# Create boundaryField entries for each STL surface
surfaces_block = ""
for stl_file in stl_files:
    base_name = os.path.splitext(stl_file)[0]
    surfaces_block += (
        f'    {base_name}\n'
        f'    {{\n'
        f'        type            omegaWallFunction;\n'
        f'        value           uniform {omega_value};\n'
        f'    }}\n\n'
    )

# Create the full omega file content
omega_content = f'''/*--------------------------------*- C++ -*----------------------------------*\\
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
    object      omega;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 -1 0 0 0 0];

internalField   uniform {omega_value};

boundaryField
{{
    inlet
    {{
        type            fixedValue;
        value           uniform {omega_value};
    }}

    "(outlet|front|back|top)"
    {{
        type            inletOutlet;
        inletValue      uniform {omega_value};
        value           uniform {omega_value};
    }}

    floor
    {{
        type            omegaWallFunction;
        value           uniform {omega_value};
    }}

{surfaces_block}    #includeEtc "caseDicts/setConstraintTypes"
}}

// ************************************************************************* //
'''

# Ensure the output directory exists
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

# Write the file
with open(output_file_path, 'w') as output_file:
    output_file.write(omega_content)

print(f"Omega boundary condition file successfully written to: {output_file_path}")
