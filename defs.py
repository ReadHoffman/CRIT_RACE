# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 17:52:09 2020

@author: Read
"""
import math
import operator

# move based on radians and distance, indexed to 0,0
def new_pos(rads, offset):
    x = math.cos(rads) * offset
    y = math.sin(rads) * offset
    return (x, y)

# add two positions together
def add_pos(pos1,pos2):
    return tuple(map(operator.add, pos1, pos2)) 

#calc hypot
def distance_between(pos1,pos2):
    return math.hypot(pos1[0]-pos2[0], pos1[1]-pos2[1])

DISPLAY_W=800
DISPLAY_H=1000

DATA_FONT_SIZE=20
DATA_FONT_COLOR = (255, 255, 255)

FPS=60

COURSE_COLOR = (255, 255, 255)

BLACK = (0, 0, 0)

BIKE_COLOR = (0, 0, 255)
BIKE_HIGHLIGHT = (255, 255, 255)
BIKE_WIDTH = 6
BIKE_HEADING_WIDTH = 2
BIKE_ACCELERATION = .02
BIKE_TURN_INCREMENT = .02
BIKE_DECELERATION = .02

NNET_INPUTS = 2
NNET_HIDDEN = 5
NNET_OUTPUTS = 1

COURSE_FILENAME = 'course_vertices.csv'
COURSE_WIDTH=40

