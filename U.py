import os
import simu

# Weather file velocity from Domus
weather_file_velocity = simu.velo

# Directory containing STL files
stl_directory = 'constant/triSurface/' 
output_file_path = '0/U'

# Normalize paths
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

stl_files = [f for f in os.listdir(stl_directory) if f.lower().endswith('.stl')]

refinement_surfaces_block = ""
for stl_file in stl_files:
    base_name = os.path.splitext(stl_file)[0]
    refinement_surfaces_block += f'    {base_name}\n    {{\n        type            noSlip;\n    }}\n\n'

U_content = f'''/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version: 12
     \\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    format      ascii;
    class       volVectorField;
    object      U;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{{
    inlet
    {{
        type            codedFixedValue;
        value           uniform (0 0 0);
        name            inletProfile; // Default value (for outlet behavior)
        
        code
        #{{
            Info << "Applying inlet velocity profile codedFixedValue" << endl;

            const fvPatch& boundaryPatch = patch();
            const vectorField& Cf = boundaryPatch.Cf();
            vectorField& field = *this;

            vector Uvec({weather_file_velocity[0]}, {weather_file_velocity[1]}, {weather_file_velocity[2]});
            
            scalar Umax = mag(Uvec);
            scalar zmax = 200.0;
            scalar alpha = 0.2;

            forAll(Cf, faceI)
            {{
                scalar z = Cf[faceI].z();
                if (z > SMALL)
                {{
                    scalar U = Umax * pow(z / zmax, alpha);
                    field[faceI] = Umax > SMALL ? U * (Uvec / Umax) : vector::zero;
                }}
                else
                {{
                    field[faceI] = vector::zero;
                }}
            }}
        #}};
      }}

    "(outlet|front|back|top)"
    {{
        type            zeroGradient;
    }}

    floor
    {{
        type            noSlip;
    }}

{refinement_surfaces_block}
    #includeEtc "caseDicts/setConstraintTypes"
}}

// ************************************************************************* //
'''

with open(output_file_path, 'w') as output_file:
    output_file.write(U_content)


print(f"U boundary condition file has been generated successfully at {output_file_path}.")
