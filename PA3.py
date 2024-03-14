"""
Control in Human-Robot Interaction Assignment 3: Pick & Place Robot for 
evaluation of motor learning with and without haptic weight rendering
-------------------------------------------------------------------------------

IMPORTANT VARIABLES
xc, yc -> x and y coordinates of the center of the haptic device and of the VR
xm -> x and y coordinates of the mouse cursor 
xh -> x and y coordinates of the haptic device (shared between real and virtual panels)
fe -> x and y components of the force fedback to the haptic device from the virtual impedances

TASKS:
1- Implement basic version of Pick & Place robot
2- Make robot pick boxes from treadmill
3- Make boxes disappear when they hit the designated field
4- Program game
5- User experiments and graphs

DEADLINES:
31st of March - Final deadline project
1st and 3rd of April - Presentations project

INSTRUCTORS: Michael Wiertlewski & Laurence Willemet & Mostafa Attala
e-mail: {m.wiertlewski,l.willemet,m.a.a.atalla}@tudelft.nl
"""

import pygame
import numpy as np
import math
import matplotlib.pyplot as plt
from pantograph import Pantograph
from box import Box
from pyhapi import Board, Device, Mechanisms
from pshape import PShape
import sys, serial, glob
from serial.tools import list_ports
import time
import random

##################### General Pygame Init #####################
##initialize pygame window
pygame.init()
window = pygame.display.set_mode((1200, 400))  ##twice 600x400 for haptic and VR
pygame.display.set_caption('Virtual Haptic Device')

screenHaptics = pygame.Surface((600, 400))
screenVR = pygame.Surface((600, 400))

##add nice icon from https://www.flaticon.com/authors/vectors-market
icon = pygame.image.load('robot.png')
pygame.display.set_icon(icon)

##add text on top to debugToggle the timing and forces
font = pygame.font.Font('freesansbold.ttf', 18)
scoreFont = pygame.font.Font('freesansbold.ttf', 28)
beginFont = pygame.font.Font('freesansbold.ttf', 30)

pygame.mouse.set_visible(True)  ##Hide cursor by default. 'm' toggles it

##set up the on-screen debugToggle
text = font.render('Virtual Haptic Device', True, (0, 0, 0), (255, 255, 255))
textRect = text.get_rect()
textRect.topleft = (10, 10)

textTime = font.render('Remaining time', True, (0, 0, 0), (255, 255, 255))
timeRect = textTime.get_rect()
timeRect.topleft = (600+20, 20)

score = font.render('Virtual Game Score', True, (0, 0, 0), (255, 255, 255))
scoreRect = score.get_rect()
scoreRect.topleft = (600+20, 40)

textinstruct = font.render('Press g and press r', True, (0, 0, 0), (255, 255, 255))
instructionRect = textinstruct.get_rect()
instructionRect.topleft = (760, 372)

textstart = font.render('Pick the first box to begin', True, (0, 0, 0), (255, 255, 255))
startRect = textstart.get_rect()
startRect.topleft = (600+200, 200)



xc, yc = screenVR.get_rect().center  ##center of the screen

##initialize "real-time" clock
clock = pygame.time.Clock()
start_ticks = pygame.time.get_ticks()
FPS = 100  # in Hertz

##define some colors
cWhite = (255, 255, 255)
cDarkblue = (36, 90, 190)
cLightblue = (0, 176, 240)
cRed = (255, 0, 0)
cOrange = (255, 100, 0)
cYellow = (255, 255, 0)
cboxRed = (190, 30, 30)
cboxBlue = (30, 30, 190)
cboxGreen = (30, 190, 30)
cplatformGreen = (20, 170, 30) # Make it a bit darker than the smaller boxes

boxes = []  # List to hold box instances
initial_x = -35  # Initial x-coord of boxes
current_score = 0  # how many boxes were placed correctly

start_time = False
time_string = ""
game_duration = 1 * 60 * 1000 # 120 seconds
remaining_time =  game_duration

##################### Init Simulated haptic device #####################

'''*********** Student should fill in ***********'''
'''*********** !Student should fill in ***********'''

####Pseudo-haptics dynamic parameters, k/b needs to be <1
k = .5  ##Stiffness between cursor and haptic display
k_spring = k / 10  ##Spring constant that is ten times lower than k
b = 0.8  ##Viscous of the pseudohaptic display

##################### Define sprites #####################

##define sprites
hhandle = pygame.image.load('handle.png')
haptic = pygame.Rect(*screenHaptics.get_rect().center, 0, 0).inflate(48, 48)
cursor = pygame.Rect(0, 0, 5, 5)
colorHaptic = cYellow

xh = np.array(haptic.center)

# platform
platform = pygame.Rect(500, 100, 50, 20)

##Set the old value to 0 to avoid jumps at init
xhold = 0
xmold = 0

# Added by Christian to initialize variable
velold = np.array([0, 0])

##Initialize velocity in the beginning to zero
vel = (0, 0)


##################### Init Virtual env. #####################

##################### Detect and Connect Physical device #####################
# USB serial microcontroller program id data:
def serial_ports():
    """ Lists serial port names """
    ports = list(serial.tools.list_ports.comports())

    result = []
    for p in ports:
        try:
            port = p.device
            s = serial.Serial(port)
            s.close()
            if p.description[0:12] == "Arduino Zero":
                result.append(port)
                print(p.description[0:12])
        except (OSError, serial.SerialException):
            pass
    return result


CW = 0
CCW = 1

haplyBoard = Board
device = Device
SimpleActuatorMech = Mechanisms
pantograph = Pantograph
robot = PShape
box = Box

#########Open the connection with the arduino board#########
port = serial_ports()  ##port contains the communication port or False if no device
if port:
    print("Board found on port %s" % port[0])
    haplyBoard = Board("test", port[0], 0)
    device = Device(5, haplyBoard)
    pantograph = Pantograph()
    device.set_mechanism(pantograph)

    device.add_actuator(1, CCW, 2)
    device.add_actuator(2, CW, 1)

    device.add_encoder(1, CCW, 241, 10752, 2)
    device.add_encoder(2, CW, -61, 10752, 1)

    device.device_set_parameters()
else:
    print("No compatible device found. Running virtual environnement...")
    # sys.exit(1)

# conversion from meters to pixels
window_scale = 3

##################### Main Loop #####################
##Run the main loop
##TODO - Perhaps it needs to be changed by a timer for real-time see: 
##https://www.pygame.org/wiki/ConstantGameSpeed

run = True
ongoingCollision = False
fieldToggle = True
robotToggle = True

debugToggle = False

grab_box = False
first_box_picked = False

haptic_free = True  # This variable is needed to avoid interacting with other boxes while other box is already grabbed

g = 9.8  # gravity constant m/s^2

 # Compute acceleration
meter_pixel_ratio = 0.0002645833 # m One pixel is moreless equal to 0.0002645833 m

def get_random_weight():
    return random.uniform(0.2, 1) # Kg

while run:

    #########Process events  (Mouse, Keyboard etc...)#########
    for event in pygame.event.get():
        ##If the window is close then quit 
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYUP:
            if event.key == ord('m'):  ##Change the visibility of the mouse
                pygame.mouse.set_visible(not pygame.mouse.get_visible())
            if event.key == ord('q'):  ##Force to quit
                run = False
            if event.key == ord('d'):
                debugToggle = not debugToggle
            if event.key == ord('g'):
                grab_box = True                               
            if event.key == ord('r'):
                grab_box = False

    # Calculate elapsed time
    if first_box_picked:

        elapsed_time = pygame.time.get_ticks() - start_ticks
        remaining_time = game_duration - elapsed_time  # 2 minutes in milliseconds - elapsed_time

        # Ensure remaining_time never goes negative
        remaining_time = max(remaining_time, 0)

        minutes = remaining_time // 60000
        seconds = (remaining_time // 1000) % 60
        milliseconds = (remaining_time % 1000) // 10  # Get the last 3 digits and scale for two decimal places display
        
        # Format the time string
        time_string = "{:02d}:{:02d}:{:02d}".format(minutes, seconds, milliseconds)
        start_time = True
    else:
        time_string = "02:00:00"

    ##Get endpoint position xh
    if port and haplyBoard.data_available():  ##If Haply is present
        # Waiting for the device to be available
        #########Read the motorangles from the board#########
        device.device_read_data()
        motorAngle = device.get_device_angles()

        #########Convert it into position#########
        device_position = device.get_device_position(motorAngle)
        xh = np.array(device_position) * 1e3 * window_scale
        xh[0] = np.round(-xh[0] + 300)
        xh[1] = np.round(xh[1] - 60)
        xm = xh  ##Mouse position is not used

    else:
        ##Compute distances and forces between blocks
        xh = np.clip(np.array(haptic.center), 0, 599)
        xh = np.round(xh)

        ##Get mouse position
        cursor.center = pygame.mouse.get_pos()
        xm = np.clip(np.array(cursor.center), 0, 599)

    '''*********** Student should fill in ***********'''

    dt = 1 / FPS
    fe = np.zeros(2)  ##Environment force is set to 0 initially.
    fb = np.zeros(2)  ##Damping force is initialized with 0
    fm = np.zeros(2)  ##Force induced by mass is initialized with 0

    ##Replace 

    ######### Compute forces ########

    # Damping
    be = 0.001  # define damping ratio

    vel = (xh - xhold) / dt  # velocity for damping


    fb[0] = be * vel[0]
    fb[1] = be * vel[1]
    
    
    acc = (vel - velold)
    
    ##Update old samples for velocity computation
    xhold = xh
    xmold = xm
    velold = vel


    ######### Graphical output #########
    ##Render the haptic surface
    screenHaptics.fill(cWhite)

    ##Change color based on effort
    colorMaster = (255, \
                   255 - np.clip(np.linalg.norm(k * (xm - xh) / window_scale) * 15, 0, 255), \
                   255 - np.clip(np.linalg.norm(k * (xm - xh) / window_scale) * 15, 0,
                                 255))  # if collide else (255, 255, 255)

    pygame.draw.rect(screenHaptics, colorMaster, haptic, border_radius=4)

    ######### Robot visualization ###################
    # update individual link position
    if robotToggle:
        robot.createPantograph(screenHaptics, xh)

    ### Hand visualisation
    screenHaptics.blit(hhandle, (haptic.topleft[0], haptic.topleft[1]))
    pygame.draw.line(screenHaptics, (0, 0, 0), (haptic.center), (haptic.center + 2 * k * (xm - xh)))

    ##Render the VR surface
    screenVR.fill(cWhite)
    '''*********** Student should fill in ***********'''
    ### here goes the visualisation of the VR sceen. 
    ### Use pygame.draw.rect(screenVR, color, rectangle) to render rectangles. 
    pygame.draw.rect(screenVR, cDarkblue, haptic, border_radius=8)
    # line(surface, color, start_pos, end_pos)
    pygame.draw.line(screenVR, (0, 0, 0), (0, 0), (0, 400))

    # Creating box objects
    if len(boxes) == 0 or (boxes[-1].x - initial_x) >= (boxes[-1].width * 4):  # 3 times width + box width itself
        new_box = Box(weight=get_random_weight(), width=30, x=initial_x)
        boxes.append(new_box)

    # drawing the conveyor belt
    pygame.draw.rect(screenVR, (100, 100, 100), (0, 300 + new_box.width, screenVR.get_width(), 35), 10, border_radius=8)

    # drawing the platform
    pygame.draw.rect(screenVR, cplatformGreen, platform)

    # Move, grab and draw the boxes
    for box in boxes:

        # If the haptic device is colliding and the user has pressed "grab", set the box in_collision state
        if haptic.colliderect(box.get_rect()) and grab_box and haptic_free:

            grab_box = True
            box.picked = True

            # First box has been picked, so game can start
            if not first_box_picked:
                start_ticks = pygame.time.get_ticks() 
                first_box_picked = True 
            haptic_free = False

        if box.picked:

            # If the user releases the box
            if not grab_box:
                # Set the box as not in_collision and the haptic as free, so it is available to grab other box
                box.picked = False
                haptic_free = True

                # correct placement detection (basic)
                if platform.colliderect(box.get_rect()) and remaining_time != 0:
                    current_score += 1

                boxes.remove(box)

            # If the box is still in_collision and grabbed
            else:
                
                # Fix the position of the box to the one of the haptic device
                box.x, box.y = haptic.x + (haptic.width - box.width) / 2, haptic.y + haptic.height
                
               
                # Compute inertia force
                # If we do not convert the acceleration to m, the fm is huge
                fm[0] += box.weight*acc[0]*meter_pixel_ratio
                fm[1] += box.weight*acc[1]*meter_pixel_ratio
                
                #Compute gravity force
                fm[1] -= g*box.weight

        else:
            box.update()

        # Draw the box
        box.draw(screenVR)
    
    # This part of the code has been placed here in order to render the forces after the update of the boxes state
    ######### Send forces to the device #########
    force = fe + fb + fm  # sum up forces
    
    if port:
       # fe[1] = -fe[1]  ##Flips the force on the Y=axis 
        force[1] = -force[1]

        ##Update the forces of the device
        device.set_device_torques(force)
        device.device_write_torques()
        # pause for 1 millisecond
        time.sleep(0.001)
    else:
        ######### Update the positions according to the forces ########
        ##Compute simulation (here there is no inertia)
        ##If the haply is connected xm=xh and dxh = 0
        dxh = (k / b * (
                xm - xh) / window_scale - force / b)  ####replace with the valid expression that takes all the forces into account
        dxh = dxh * window_scale
        xh = np.round(xh + dxh)  ##update new positon of the end effector

    haptic.center = xh
    
    #########
    

    ##Fuse it back together
    window.blit(screenHaptics, (0, 0))
    window.blit(screenVR, (600, 0))

    ##Print status in  overlay
    if debugToggle:
        text = font.render("FPS = " + str(round(clock.get_fps())) + \
                           "  xm = " + str(np.round(10 * xm) / 10) + \
                           "  xh = " + str(np.round(10 * xh) / 10) + \
                           "  fe = " + str(np.round(10 * fe) / 10) + \
                           "  fb = " + str(np.round(10 * fb) / 10) + \
                           "  fm = " + str(np.round(10 * fm) / 10) \
                           , True, (0, 0, 0), (255, 255, 255))
        window.blit(text, textRect)

    if not first_box_picked:
        textstart = font.render("Pick up the first box to start", True, (0, 0, 0), (255, 255, 255))
        window.blit(textstart, startRect)
    if remaining_time == 0:
        textstart = font.render("Nice job!", True, (0, 0, 0), (255, 255, 255))
        startRect.topleft = (600+270, 180)
        window.blit(textstart, startRect)

    texttime = font.render("Remaining time: " + time_string, True, (0, 0, 0), (255, 255, 255))
    window.blit(texttime, timeRect)

    score = font.render("Score: " + str(round(current_score)), True, (0, 0, 0), (255, 255, 255))
    window.blit(score, scoreRect)

    textinstruct = font.render("Press g to grab and r to release", True, (0, 0, 0), (255, 255, 255))
    window.blit(textinstruct, instructionRect)


    pygame.display.flip()
    ##Slow down the loop to match FPS
    clock.tick(FPS)

pygame.display.quit()
pygame.quit()
