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
from pyhapi import Board, Device, Mechanisms
from pshape import PShape
import sys, serial, glob
from serial.tools import list_ports
import time
import random


##################### General Pygame Init #####################
##initialize pygame window
pygame.init()
window = pygame.display.set_mode((1200, 400))   ##twice 600x400 for haptic and VR
pygame.display.set_caption('Virtual Haptic Device')

screenHaptics = pygame.Surface((600,400))
screenVR = pygame.Surface((600,400))

##add nice icon from https://www.flaticon.com/authors/vectors-market
icon = pygame.image.load('robot.png')
pygame.display.set_icon(icon)

##add text on top to debugToggle the timing and forces
font = pygame.font.Font('freesansbold.ttf', 18)

pygame.mouse.set_visible(True)     ##Hide cursor by default. 'm' toggles it
 
##set up the on-screen debugToggle
text = font.render('Virtual Haptic Device', True, (0, 0, 0),(255, 255, 255))
textRect = text.get_rect()
textRect.topleft = (10, 10)


xc,yc = screenVR.get_rect().center ##center of the screen


##initialize "real-time" clock
clock = pygame.time.Clock()
FPS = 100   #in Hertz

##define some colors
cWhite = (255,255,255)
cDarkblue = (36,90,190)
cLightblue = (0,176,240)
cRed = (255,0,0)
cOrange = (255,100,0)
cYellow = (255,255,0)
cboxRed = (190, 30, 30)
cboxBlue = (30, 30, 190)
cboxGreen = (30, 190, 30)


##################### Init Simulated haptic device #####################

'''*********** Student should fill in ***********'''

####Virtual environment -  Wall


####Virtual environment -  Force fieldToggle f(x,y)


##Compute the height map and the gradient along x and y



'''*********** !Student should fill in ***********'''


####Pseudo-haptics dynamic parameters, k/b needs to be <1
k = .5              ##Stiffness between cursor and haptic display
k_spring = k/10     ##Spring constant that is ten times lower than k
b = 0.8            ##Viscous of the pseudohaptic display


##################### Define sprites #####################

##define sprites
hhandle = pygame.image.load('handle.png')
haptic  = pygame.Rect(*screenHaptics.get_rect().center, 0, 0).inflate(48, 48)
cursor  = pygame.Rect(0, 0, 5, 5)
colorHaptic = cDarkblue

xh = np.array(haptic.center)

##Set the old value to 0 to avoid jumps at init
xhold = 0
xmold = 0

# Added by Christian to initialize variable
velold = np.array([0,0])

##Initialize velocity in the beginning to zero
vel = (0,0)


##################### Init Virtual env. #####################

'''*********** !Student should fill in ***********'''

def get_random_color():
    return {
        1: cboxRed,
        2: cboxBlue,
        3: cboxGreen
    }[random.randint(1, 3)]

box_velocity = 1.2 # pixels per frame
box_color = (0,0,0) # initialize box color as black

list_colors = [get_random_color() for _ in range(6)]

# Create boxes 
box_width, box_height = 35, 35
boxes = [{'x': -3*i*box_width, 'y': 300, 'width': box_width, 'height': box_height, 'color': color, 'in_collision': False} for i, color in enumerate(list_colors)]


'''*********** !Student should fill in ***********'''


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
   

#########Open the connection with the arduino board#########
port = serial_ports()   ##port contains the communication port or False if no device
if port:
    print("Board found on port %s"%port[0])
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
    #sys.exit(1)
    

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

haptic_free = True # This variable is needed to avoid interacting with other boxes while other box is already grabbed
    
while run:
        
    #########Process events  (Mouse, Keyboard etc...)#########
    for event in pygame.event.get():
        ##If the window is close then quit 
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYUP:
            if event.key == ord('m'):   ##Change the visibility of the mouse
                pygame.mouse.set_visible(not pygame.mouse.get_visible())  
            if event.key == ord('q'):   ##Force to quit
                run = False            
            if event.key == ord('d'):
                debugToggle = not debugToggle
            if event.key == ord('r'):
                robotToggle = not robotToggle
            if event.key == ord('g'):
                grab_box = not grab_box
            '''*********** Student can add more ***********'''
            ##Toggle the wall or the height map
            

            '''*********** !Student can add more ***********'''

    ######### Read position (Haply and/or Mouse)  #########
    

    ##Get endpoint position xh
    if port and haplyBoard.data_available():    ##If Haply is present
        #Waiting for the device to be available
        #########Read the motorangles from the board#########
        device.device_read_data()
        motorAngle = device.get_device_angles()
        
        #########Convert it into position#########
        device_position = device.get_device_position(motorAngle)
        xh = np.array(device_position)*1e3*window_scale
        xh[0] = np.round(-xh[0]+300)
        xh[1] = np.round(xh[1]-60)
        xm = xh     ##Mouse position is not used
         
    else:
        ##Compute distances and forces between blocks
        xh = np.clip(np.array(haptic.center),0,599)
        xh = np.round(xh)
        
        ##Get mouse position
        cursor.center = pygame.mouse.get_pos()
        xm = np.clip(np.array(cursor.center),0,599)
    
    '''*********** Student should fill in ***********'''
    
    dt = 1/FPS
    fe = np.zeros(2)  ##Environment force is set to 0 initially.
    fb = np.zeros(2)  ##Damping force is initialized with 0
    fm = np.zeros(2)  ##Force induced by mass is initialized with 0

    ##Replace 
    
    ######### Compute forces ########
    
    # Elastic impedance
    img_center = np.array((300, 200))
    cursor_center = np.array(cursor.center)  # Convert cursor.center to a NumPy array
    fe = (cursor_center - img_center) * k_spring

    
    # Damping and masses
    
    #Damping
    be = 0.001 #define damping ratio
    
    vel = (xh-xhold)/dt #velocity for damping

    fb[0] = be * vel[0]
    fb[1] = be * vel[1]

    #Mass
    mass = 0.001

    acc = (vel-velold)
    fm[0] = mass*acc[0]
    fm[1] = mass*acc[1]


    ##Update old samples for velocity computation
    xhold = xh
    xmold = xm
    velold = vel

    '''*********** !Student should fill in ***********'''
    
    ######### Send forces to the device #########
    if port:
        fe[1] = -fe[1]  ##Flips the force on the Y=axis 
        
        ##Update the forces of the device
        device.set_device_torques(fe)
        device.device_write_torques()
        #pause for 1 millisecond
        time.sleep(0.001)
    else:
        ######### Update the positions according to the forces ########
        ##Compute simulation (here there is no inertia)
        ##If the haply is connected xm=xh and dxh = 0
        force = fe + fb - fm #sum up forces
        dxh = (k/b*(xm-xh)/window_scale -force/b)    ####replace with the valid expression that takes all the forces into account
        dxh = dxh*window_scale
        xh = np.round(xh+dxh)             ##update new positon of the end effector


    haptic.center = xh 


    ######### Graphical output #########
    ##Render the haptic surface
    screenHaptics.fill(cWhite)
    
    ##Change color based on effort
    colorMaster = (255,\
         255-np.clip(np.linalg.norm(k*(xm-xh)/window_scale)*15,0,255),\
         255-np.clip(np.linalg.norm(k*(xm-xh)/window_scale)*15,0,255)) #if collide else (255, 255, 255)

        
    pygame.draw.rect(screenHaptics, colorMaster, haptic, border_radius=4)
    

    ######### Robot visualization ###################
    # update individual link position
    if robotToggle:
        robot.createPantograph(screenHaptics,xh)
        
    
    ### Hand visualisation
    screenHaptics.blit(hhandle,(haptic.topleft[0],haptic.topleft[1]))
    pygame.draw.line(screenHaptics, (0, 0, 0), (haptic.center),(haptic.center+2*k*(xm-xh)))
    
    
    ##Render the VR surface
    screenVR.fill(cWhite)
    '''*********** Student should fill in ***********'''
    ### here goes the visualisation of the VR sceen. 
    ### Use pygame.draw.rect(screenVR, color, rectangle) to render rectangles. 
    pygame.draw.rect(screenVR, colorHaptic, haptic, border_radius=8)
    #line(surface, color, start_pos, end_pos)
    pygame.draw.line(screenVR, (0,0,0), (0,0), (0,400))


    # Move, grab and draw the boxes
    for box in boxes:
        
        # Create rect object of the box in order to apply pygame collision logic
        box_rect = pygame.Rect(box['x'], box['y'], box['width'], box['height'])
        
        # If the haptic device is colliding and the user has pressed "grab", set the box in_collision state
        if haptic.colliderect(box_rect) and grab_box and haptic_free:
            box['in_collision'] = True
            haptic_free = False
        
        if box['in_collision']:
            
            # If the user releases the box
            if not grab_box:
                # Set the box as not in_collision and the haptic as free, so it is available to grab other box
                box['in_collision'] = False
                haptic_free = True
                
                # Reset the position and color of the box
                box_rect.x = -box_width
                box_rect.y = 300
                box['color'] = get_random_color() 
            
            # If the box is still in_collision and grabbed, fix the position of the box to the one of the haptic device
            else:
                box_rect.midtop = haptic.midbottom
            
        else:
            # If the box is not in collision, update its velocity
            box_rect.x += box_velocity
        
            # If the box has moved off the screen, reset its position to the left and assign new random color
            if box_rect.x > 600:
               box_rect.x = -box_width
               box_rect.y = 300
               box['color'] = get_random_color()  
            
        # Update the x and y positions of the box   
        box['x'] = box_rect.x
        box['y'] = box_rect.y
        
        # Draw the box
        pygame.draw.rect(screenVR, box['color'], box_rect)
    

    
    
    '''*********** !Student should fill in ***********'''


    ##Fuse it back together
    window.blit(screenHaptics, (0,0))
    window.blit(screenVR, (600,0))

    ##Print status in  overlay
    if debugToggle: 
        
        text = font.render("FPS = " + str(round(clock.get_fps())) + \
                            "  xm = " + str(np.round(10*xm)/10) +\
                            "  xh = " + str(np.round(10*xh)/10) +\
                            "  fe = " + str(np.round(10*fe)/10) +\
                            "  fb = " + str(np.round(10*fb)/10) +\
                            "  fm = " + str(np.round(10*fm)/10) \
                            , True, (0, 0, 0), (255, 255, 255))
        window.blit(text, textRect)


    pygame.display.flip()    
    ##Slow down the loop to match FPS
    clock.tick(FPS)

pygame.display.quit()
pygame.quit()

