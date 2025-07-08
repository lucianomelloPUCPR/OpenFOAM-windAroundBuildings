import simu

control_dict_path = 'system/controlDict'

control_dict_content = f'''/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website: https://openfoam.org
    \\  /    A nd           | Version: 12
     \\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    format      ascii;
    class       dictionary;
    object      controlDict;
}}

application     foamRun;

solver          fluid;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         {simu.endTime};

deltaT          {simu.deltat};

writeControl    timeStep;

writeInterval   {simu.interval};

purgeWrite      0;

writeFormat     ascii;

writePrecision  10;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable yes;

libs ("libfieldFunctionObjects.so");

functions
{{
    #include "functions"
}}
'''

with open(control_dict_path, 'w') as control_dict_file:
    control_dict_file.write(control_dict_content)

print(f"ControlDict written to {control_dict_path}")
