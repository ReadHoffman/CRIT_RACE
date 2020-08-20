# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 19:42:30 2020

@author: Read
"""
import math
import pygame
import operator
from defs import *
from nnet import Nnet

# move based on radians and distance, indexed to 0,0
def new_pos(rads, offset):
    x = math.cos(rads) * offset
    y = math.sin(rads) * offset
    return (x, y)

# add two positions together
def add_pos(pos1,pos2):
    return tuple(map(operator.add, pos1, pos2)) 

class Bike:
    def __init__(self,gameDisplay):
        self.gameDisplay = gameDisplay
        self.color = BIKE_COLOR
        self.highlight = BIKE_HIGHLIGHT
        self.radius = BIKE_WIDTH
        self.pos = (DISPLAY_W*5/10,DISPLAY_H*2/10)
        self.vector = (0,0)
        self.radians_heading = 0
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.fitness = 0
        self.time_lived = 0
        self.nnet = Nnet(NNET_INPUTS, NNET_HIDDEN, NNET_OUTPUTS)
        self.dist_forward = 0
        self.dist_right = 0
        self.dist_left = 0
        self.dist_forward_right = 0
        self.dist_forward_left = 0
        self.dist_forward_prior = 0
        self.dist_right_prior = 0
        self.dist_left_prior = 0
        self.dist_forward_right_prior = 0
        self.dist_forward_left_prior = 0
    
    def bike_line(self):
        start_pos = add_pos(new_pos(self.radians_heading,self.radius),self.pos)
        end_pos = add_pos(new_pos(self.radians_heading+math.pi,self.radius),self.pos)
        return (start_pos,end_pos)
    
    def draw(self):
        pygame.draw.circle(self.gameDisplay, self.color, (int(self.pos[0]),int(self.pos[1])), self.radius)
        start_pos, end_pos = self.bike_line()
        pygame.draw.line(self.gameDisplay, self.highlight, start_pos, end_pos, BIKE_HEADING_WIDTH)
        
    def update(self):
#        self.update_vector(self.nnet.get_outputs(self.get_inputs()))
        self.draw()
    
    def update_vector(self,outputs):
        if self.up==True: w=-.02 
        else: w=0
        if self.left==True: a=-.02
        else: a=0
        if self.down==True: s=.02
        else: s=0
        if self.right==True: d=.02
        else: d=0
        ws = w+s
        ad = a+d
        self.vector = ((self.vector[0]+ad),(self.vector[1]+ws))

    def update_pos(self):
        self.pos = tuple(map(operator.add, self.pos, self.vector))

    def update_inputs(self, course):
        #create a way to update all the measurements in get_inputs
        pass

    def get_inputs(self):
        inputs = [
            self.dist_forward,
            self.dist_right,
            self.dist_left,
            self.dist_forward_right,
            self.dist_forward_left,
            self.dist_forward_prior,
            self.dist_right_prior,
            self.dist_left_prior,
            self.dist_forward_right_prior,
            self.dist_forward_left_prior,
        ]

        return inputs