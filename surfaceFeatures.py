import os

# Directory containing STL files
stl_directory = 'constant/triSurface/' 

# Path to the output surfaceFeaturesDict file
output_file_path = 'system/surfaceFeaturesDict'

# Normalize paths
stl_directory = os.path.normpath(stl_directory)
output_file_path = os.path.normpath(output_file_path)

# Find all STL files in the specified directory
stl_files = [f for f in os.listdir(stl_directory) if f.lower().endswith('.stl')]

# Construct the surfaces list in the required format
surfaces_list = ' '.join([f'\n\t\t\t\t"{stl_file}"' for stl_file in stl_files])

# Define the content of the surfaceFeaturesDict file
surface_features_dict_content = f'''/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  10
     \\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    format      ascii;
    class       dictionary;
    object      surfaceFeaturesDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

surfaces ({surfaces_list});

#includeEtc "caseDicts/surface/surfaceFeaturesDict.cfg"

// ************************************************************************* //
'''

# Write the generated content to the surfaceFeaturesDict file
with open(output_file_path, 'w') as output_file:
    output_file.write(surface_features_dict_content)

print(f"surfaceFeaturesDict file has been generated successfully at {output_file_path}.")
