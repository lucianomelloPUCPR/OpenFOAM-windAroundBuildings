import os

# === CONFIGURATION ===
Uref = 3.0             # Reference inlet velocity magnitude in m/s
I = 0.05               # Turbulence intensity (5% typical for external flows)
k_value = 1.5 * (Uref * I)**2  # Turbulence kinetic energy

# === PATHS ===
stl_directory = 'constant/triSurface/'
output_file_path = '0/k'

# Normalize paths
stl_directory = os.path.normpath(stl_directory)
output_file_path = os.path.normpath(output_file_path)

# Find all STL files in the specified directory
stl_files = [f for f in os.listdir(stl_directory) if f.lower().endswith('.stl')]

# Prepare boundary block for STL patches
refinement_surfaces_block = ""
for stl_file in stl_files:
    base_name = os.path.splitext(stl_file)[0]
    refinement_surfaces_block += (
        f'    {base_name}\n'
        f'    {{\n'
        f'        type            kqRWallFunction;\n'
        f'        value           uniform {k_value:.2g};\n'
        f'    }}\n\n'
    )

# Template for k field
k_content = f'''/*--------------------------------*- C++ -*----------------------------------*\\
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
    object      k;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform {k_value:.2g};

boundaryField
{{
    inlet
    {{
        type            inletOutlet;
        inletValue      uniform {k_value:.2g};
        value           uniform {k_value:.2g};
    }}

    "(outlet|front|back|top)"
    {{
        type            inletOutlet;
        inletValue      uniform {k_value:.2g};
        value           uniform {k_value:.2g};
    }}

    floor
    {{
        type            kqRWallFunction;
        value           uniform {k_value:.2g};
    }}

{refinement_surfaces_block}    #includeEtc "caseDicts/setConstraintTypes"
}}

// ************************************************************************* //
'''

# Write the content to the k file
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
with open(output_file_path, 'w') as output_file:
    output_file.write(k_content)

print(f"k field written successfully to: {output_file_path}")
#print(f"k value based on Uref = {Uref} m/s and I = {I:.2%} is: {k_value:.2g}")
