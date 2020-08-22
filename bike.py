# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 19:42:30 2020

@author: Read
"""
import random
import math
import pygame
import operator
from defs import *
from nnet import Nnet
from course import Course #test
from shapely.geometry import LineString





class Bike:
    def __init__(self,gameDisplay):
        self.gameDisplay = gameDisplay
        self.color = BIKE_COLOR
        self.highlight = BIKE_HIGHLIGHT
        self.radius = BIKE_WIDTH
        self.pos = (DISPLAY_W*5/10,DISPLAY_H*2/10)
        self.vector = (0,0)
        self.speed = 0
        self.radians_heading = 0
        self.forward = True
        self.brake = False
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
        self.alive = True
    
    def bike_line(self):
        start_pos = add_pos(new_pos(self.radians_heading,self.radius),self.pos)
        end_pos = add_pos(new_pos(self.radians_heading+math.pi,self.radius),self.pos)
        return (start_pos,end_pos)
    
    
    def draw(self):
        pygame.draw.circle(self.gameDisplay, self.color, (int(self.pos[0]),int(self.pos[1])), self.radius)
        start_pos, end_pos = self.bike_line()
        pygame.draw.line(self.gameDisplay, self.highlight, start_pos, end_pos, BIKE_HEADING_WIDTH)
        
    def update(self,course):
#        self.nnet.get_outputs(self.get_inputs())
        self.draw()
        self.update_vector()
        self.check_collision(course)
        self.update_pos()
        
    
    def update_vector(self):
        if self.alive:
            
#            self.forward = bool(random.getrandbits(1))
            self.brake = bool(random.getrandbits(1))
            self.left = bool(random.getrandbits(1))
            self.right = bool(random.getrandbits(1))
            
            if self.forward==True: self.speed += .02 
            if self.left==True: self.radians_heading -= .02
            if self.brake==True: self.speed = max([self.speed-.02,0])
            if self.right==True: self.radians_heading += .02
            self.vector = new_pos(self.radians_heading,self.speed)

    def update_pos(self):
        if self.alive:
            self.pos = tuple(map(operator.add, self.pos, self.vector))

    def update_inputs(self, course):
        #create a way to update all the measurements in get_inputs
        pass
    
    def check_collision(self,course):
        course_lines_list = [course.inner_verticies,course.outer_verticies]
        
        for course_lines in course_lines_list:
            course_lines_len = len(course_lines)
            
            for i, course_line in enumerate(course_lines):
                start_point = course_line
                if i+1==course_lines_len: end_point = course_lines[0]
                else: end_point = course_lines[i+1]
                
                bike_start,bike_end = self.bike_line()
                
                line = LineString([(bike_start),(bike_end)]) #LineString([(0, 0), (1, 1)])
                other = LineString([(start_point),(end_point)]) #LineString([(0, 1), (1, 0)])
                
                
                if line.intersects(other):
#                    print("Crash")
                    self.speed = 0
                    self.vector = (0,0)
                    self.alive = False
                    
                    self.color = (0,255,0) #test


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