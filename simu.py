# Domain - times greater than the highest building
domainExpansionXY = 4.5
domainExpansionZ = 4.5
paddingDomain = 0.2

# Mesh 
cells = 30
refinementBox = 2
refinementSurface1 = 2
refinementSurface2 = 2
surfaceLayers = 6
eMeshLevel = 3

# Velocity - from Domus
velo = [3, 0, 0]

# Weather Temperature
T = 300

# Wall temperature
Tw = 292.15

# Floor temperature
Tf = 290.0

# Demand power for heating from Domus - air conditionning system 
# Including the power at gradient 'gradient        uniform <value>;'
rejectedHeat = 122.0 # [W/m2]

# Sensors - distance from the wall
projectionDistance = 0.01 #[m]

# Simulation
interval = 10
endTime = 100
deltat = 1
