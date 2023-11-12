import math
import random

('''
1 pick an equation qroup (chapter, difficultly, related)
2 pick equation
3 pick which variable to solve for
4 assign other variables/standards
5 print variables and meanings
6 input for solution (test for correctness?)
7 display solution and equation?
8 reset
''')

#options

displayEquation = True
cycleGroups = True
chosenGroups = [
    'chapter1',
    'chapter2',
]

#constants
G = 6.67 * (10 ** -11)
R = 8.314 # J/mol
pi=math.pi
gravityConstant = 9.81

#variable

force = 0
mass = 0
acceleration = 0
momentum = 0 
velocity = 0
changeInMomentum = 0
forceOfGravity = 0
mass1 = 0
mass2 = 0
radius = 0
work = 0
distance = 0
power = 0
time = 0
density = 0
pressure = 0
temperature = 0
speed = 0
initialVelocity = 0
finalVelocity = 0
relativeDensity = 0
densityAtSeaLevel = 0
staticPressure = 0
dynamicPressure = 0
stagnationPressure = 0
height = 0
coefficientOfDrag = 0
coefficientOfLift = 0
coefficentOfPitchingMoment = 0
lift = 0
drag = 0
pitchingMoment = 0
liftToDragRatio = 0
frontalArea = 0
planArea = 0
chordLength = 0
positionOnChord = 0
coefficentOfPitchingMomentAboutAeroCenter = 0
coefficentOfPitchingMomentAboutLeadingEdge = 0
AOA = 0
leverageOfLift = 0
leverageofDrag = 0
coefficientOfInducedDrag = 0
inducedDrag = 0
thrust = 0
weight = 0
advancePerRevolution = 0
slip = 0
practicalPitch = 0
idealPitch = 0
efficiencyOfPropeller = 0
workByEngine = 0
workByPropeller = 0
torque = 0
liftOnWings = 0
liftOnTail = 0
totalLift = 0 
conversionFactor = 0
noseDownMoment = 0
noseUpMoment = 0
totalDrag = 0
remainderDrag = 0

#equation groups
cycleGroupsList = [
    'chapter1',
    'chapter2',
    'chapter3',
    'chapter4',
    'chapter5',
    'chapter6',
    'chapter7',
    'kinematics',
    'basicPhysics',
    'forcesOnPlane',  # = chapter3?
]

allGroups = {
    'chapter1' : (1,2),
    'chapter2' : (1,2),
    'chapter3' : (1,2),
    'chapter4' : (1,2),
    'chapter5' : (1,2),
    'chapter6' : (1,2),
    'chapter7' : (1,2),
    'kinematics' : (1,2),
    'basicPhysics' : (1,2),
    'forcesOnPlane' : (1,2), # = chapter3?
}

#equations and variables

def fma(force,mass,acceleration):
    if displayEquation == True:
        print("Force = Mass * Acceleration")
    #i need to declare all the variales than add them to a list and than check for the variableSelect

def play():
    if cycleGroups == True :
        groupSelect = random.choice(cycleGroupsList)
    elif cycleGroups == False :
        groupSelect = random.choice(chosenGroups)
    equationSelect = random.choice(allGroups[groupSelect])
    variableSelect = random.choice(variableList)
    print(groupSelect, equationSelect, variableSelect)

play()
