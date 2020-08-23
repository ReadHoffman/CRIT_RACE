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
import shapely
from shapely.geometry import LineString, Point



class Bike:
    def __init__(self,gameDisplay,pos):
        self.gameDisplay = gameDisplay
        self.color = BIKE_COLOR
        self.highlight = BIKE_HIGHLIGHT
        self.radius = BIKE_WIDTH
        self.pos = pos
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
        self.dist_ahead = 0
        self.dist_right = 0
        self.dist_left = 0
        self.dist_ahead_right = 0
        self.dist_ahead_left = 0
        self.dist_back = 0
#        self.dist_forward_prior = 0
#        self.dist_right_prior = 0
#        self.dist_left_prior = 0
#        self.dist_forward_right_prior = 0
#        self.dist_forward_left_prior = 0
        self.alive = True
        
        #vision
        self.wall_intersect_points = [(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)] #idea
        self.vision_radian_delta = [0,-math.pi/2,math.pi/2,-math.pi/4,math.pi/4,math.pi]
#        self.wall_ahead_point = (0,0)
#        self.wall_right_point = (0,0)
#        self.wall_left_point = (0,0)
#        self.wall_ahead_right_point = (0,0)
#        self.wall_ahead_left_point = (0,0)
#        self.wall_back_point = (0,0)
    
    def bike_line(self):
        start_pos = add_pos(new_pos(self.radians_heading,self.radius),self.pos)
        end_pos = add_pos(new_pos(self.radians_heading+math.pi,self.radius),self.pos)
        return (start_pos,end_pos)
    
    def get_vision_intersection_point(self,course):
        vision_points = self.wall_intersect_points
#        vision_points = [self.wall_ahead_point,self.wall_right_point,self.wall_left_point, \
#                         self.wall_ahead_right_point,self.wall_ahead_left_point,self.wall_back_point]
#        vision_radian_delta = [0,-math.pi/2,math.pi/2,-math.pi/4,math.pi/4,math.pi]
        vision_distances = [self.dist_ahead, self.dist_right, self.dist_left, self.dist_ahead_right, self.dist_ahead_left, self.dist_back ]
        
        for j in range(len(vision_points)):
            line1_start = self.bike_line()[0]
            line1_end = add_pos(new_pos(self.radians_heading+self.vision_radian_delta[j],VISION_LINE_LENGTH_MAX),line1_start)
            
            course_points_list = [course.inner_verticies,course.outer_verticies]
            
            intersections = []
            for course_points in course_points_list:
                course_points_len = len(course_points)
                
                for i, course_point in enumerate(course_points):
                    line2_start = course_point
                    if i+1==course_points_len: line2_end = course_points[0]
                    else: line2_end = course_points[i+1]
            
#                    intersection = lines_intersect_pos(line1_start,line1_end,line2_start,line2_end)
                    intersection= lines_intersect_pos(line1_start, line1_end, line2_start, line2_end)
                    if intersection!=None:
                        intersections.append(intersection)
            
            #find closest
            intersections_dist =[]
            for intersection in intersections:
                intersections_dist.append(distance_between(line1_start,intersection))
                
            min_dist = min(intersections_dist) 
            min_indices = [k for k, intersection_dist in enumerate(intersections_dist) if intersection_dist == min_dist] 
            
            vision_points[j] = intersections[min(min_indices)]
            vision_distances[j] = intersections_dist[min(min_indices)]

#    def update_vision_dist(self):
#        bike_leading_point = self.bike_line()[0]
#        vision_points = [self.wall_ahead_point,self.wall_right_point,self.wall_left_point, \
#                         self.wall_ahead_right_point,self.wall_ahead_left_point,self.wall_back_point]
#        [print(vision_point) for vision_point in vision_points]
#        
#        vision_distances = [self.dist_ahead, self.dist_right, self.dist_left, self.dist_ahead_right, self.dist_ahead_left, self.dist_back ]
#        
#        for i in range(len(vision_points)):
##            print(vision_points[i])
#            vision_distances[i] = distance_between(bike_leading_point,vision_points[i])
            
    
    def draw(self):
        pygame.draw.circle(self.gameDisplay, self.color, (int(self.pos[0]),int(self.pos[1])), self.radius)
        start_pos, end_pos = self.bike_line()
        pygame.draw.line(self.gameDisplay, self.highlight, start_pos, end_pos, BIKE_HEADING_WIDTH)
        
        bike_leading_point = self.bike_line()[0]
        [pygame.draw.line(self.gameDisplay, VISION_COLOR, bike_leading_point, wall_intersect_point, VISION_WIDTH) for wall_intersect_point in self.wall_intersect_points]
        
        
    def update(self,course):
#        self.nnet.get_outputs(self.get_inputs())
        self.get_vision_intersection_point(course)
#        self.update_vision_dist()
        self.draw()
        self.update_vector()
        self.check_collision(course)
        self.update_pos()
        
    
    def update_vector(self):
        if self.alive:
            
            self.forward = bool(random.getrandbits(1))
            self.brake = bool(random.getrandbits(1))
            self.left = bool(random.getrandbits(1))
            self.right = bool(random.getrandbits(1))
            
            if self.forward==True : self.speed += .02 
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