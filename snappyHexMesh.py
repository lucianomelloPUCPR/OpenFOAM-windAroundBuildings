import os
import blockMesh  # Assuming blockMesh.py provides xmin, xmax, ymin, ymax, zmin, zmax
import surfaceFeatures # Generating eMesh files
import simu

# Directory containing STL files
stl_directory = 'constant/triSurface/'

# Path to the output snappyHexMeshDict file
output_file_path = 'system/snappyHexMeshDict'

# Normalize paths
stl_directory = os.path.normpath(stl_directory)
output_file_path = os.path.normpath(output_file_path)

# Find all STL files in the specified directory
stl_files = [f for f in os.listdir(stl_directory) if f.lower().endswith('.stl')]

# Import the bounding box values from blockMesh.py
xmin, xmax, ymin, ymax, zmin, zmax = blockMesh.x_min, blockMesh.x_max, blockMesh.y_min, blockMesh.y_max, blockMesh.z_min, blockMesh.z_max
xmin_geo, xmax_geo, ymin_geo, ymax_geo, zmin_geo, zmax_geo = blockMesh.x_min_geo, blockMesh.x_max_geo, blockMesh.y_min_geo, blockMesh.y_max_geo, blockMesh.z_min_geo, blockMesh.z_max_geo

# Calculate the insidePoint, slightly offset from one corner to be inside the domain
offset = 0.01  # Small offset to ensure the point is inside
inside_x = round(float(xmin) + offset, 2)
inside_y = round(float(ymin) + offset, 2)
inside_z = round(float(zmin) + offset, 2)

# Construct the geometry and castellatedMeshControls sections
geometry_entries = ""
refinement_Box = ""
features_entries = ""
layers_entries = ""
refinement_surfaces_entries = []

for stl_file in stl_files:
    base_name = os.path.splitext(stl_file)[0]
    geometry_entries += f"    {base_name}\n    {{\n        type triSurfaceMesh;\n        file \"{stl_file}\";\n    }}\n"
    features_entries += f"      {{ file  \"{base_name}.eMesh\"; level {simu.eMeshLevel}; }}\n"
    refinement_surfaces_entries.append(base_name)
    layers_entries += f"    {base_name}\n    {{\n        nSurfaceLayers {simu.surfaceLayers};\n    }}\n"

refinement_Box = f"""      refinementBox
      {{
          type searchableBox;
          min ({xmin_geo} {ymin_geo} {zmin_geo});
          max ({xmax_geo} {ymax_geo} {zmax_geo});

      }}
"""
refinement_surfaces_block = f"""
        "({"|".join(refinement_surfaces_entries)})"
        {{
            level ({simu.refinementSurface1} {simu.refinementSurface2}) ;
            patchInfo {{ type wall; }}
        }}
"""

# Define the content of the snappyHexMeshDict file
snappy_hex_mesh_dict_content = f'''/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  12
     \\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    format      ascii;
    class       dictionary;
    object      snappyHexMeshDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#includeEtc "caseDicts/mesh/generation/snappyHexMeshDict.cfg"

castellatedMesh on;
snap            on;
addLayers       off;

geometry
{{
{geometry_entries}

{refinement_Box}
}};


castellatedMeshControls
{{
    nCellsBetweenLevels 3;

    features
    (
{features_entries}
    );

    refinementSurfaces
    {{
{refinement_surfaces_block}
    }}

    refinementRegions
    {{
         refinementBox
        {{
            mode    inside;
            level   {simu.refinementBox};
        }}
    }}

    insidePoint ({inside_x} {inside_y} {inside_z});  // Automatically calculated inside the domain
    allowFreeStandingZoneFaces true;
}}

snapControls
{{
    nSmoothPatch 3;
    tolerance 2.0;
    nSolverIter 300;
    nRelaxIter 5;
    explicitFeatureSnap    true;
    implicitFeatureSnap    false;
}}

addLayersControls
{{
    layers
    {{
{layers_entries}
    }}        
    

    relativeSizes       true;
    expansionRatio      1.2;
    finalLayerThickness 0.5;
    minThickness        1e-3;
}}

meshQualityControls
{{
    #include "meshQualityDict"

    relaxed
    {{
        maxnonOrtho 75;
    }}

    nSmoothScale 75;
    errorReduction 0.75;
}}

writeFlags
(
    // scalarLevels
    // layerSets
    // layerFields
);

mergeTolerance 1e-6;

// ************************************************************************* //
'''

# Write the generated content to the snappyHexMeshDict file
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
with open(output_file_path, 'w') as output_file:
    output_file.write(snappy_hex_mesh_dict_content)

print(f"snappyHexMeshDict file has been generated successfully at {output_file_path}.")
