# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 18:36:46 2020

@author: Read
"""
import pygame
from defs import *
import math
import operator
import csv
from shapely.geometry import LineString

class Course_Point:
    def __init__(self,pos,i):
        self.pos = pos
        self.i = i
        self.diameter = COURSE_WIDTH
        self.radius = self.diameter/2
        self.radians_lag_lead = 0
        self.radians_lag_lead2 = 0
        self.end_point = False
        self.distance_prior_point = 0
        self.distance_next_point = 0
        self.pos_left = 0
        self.pos_right = 0

class Course:
    def __init__(self,gameDisplay):
        self.gameDisplay = gameDisplay
        self.outer_num = 8
        self.inner_num = 8
        self.course_width = COURSE_WIDTH
        self.course_points = []
        self.outer_verticies = [] #[(DISPLAY_W*1/10,DISPLAY_H*1/10),(DISPLAY_W*9/10,DISPLAY_H*1/10),(DISPLAY_W*9/10,DISPLAY_H*9/10),(DISPLAY_W*1/10,DISPLAY_H*9/10),(DISPLAY_W*1/10,DISPLAY_H*1/10)]
        self.inner_verticies = [] #[(DISPLAY_W*3/10,DISPLAY_H*3/10),(DISPLAY_W*7/10,DISPLAY_H*3/10),(DISPLAY_W*7/10,DISPLAY_H*7/10),(DISPLAY_W*3/10,DISPLAY_H*7/10),(DISPLAY_W*3/10,DISPLAY_H*3/10)]
    
    def import_course(self):
        with open(COURSE_FILENAME,newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            loaded_points = []
            for row in reader:
#                data = (int(row["index"]),int(row["x"]), int(row["y"]))
                point = Course_Point( ( int(row["x"]),int(row["y"]) ) , int(row["i"]) )
                loaded_points.append(point)
            self.course_points = loaded_points
            
    def create_course_points(self,click,mouse_pos):
        if click==True:
            new_point_check = [distance_between(mouse_pos,course_point.pos) > self.course_width/2 for course_point in self.course_points ]
            if len(new_point_check)==0 or all(new_point_check):
                point = Course_Point(mouse_pos,len(self.course_points))
                self.course_points.append(point)
    
    def load_course(self):
        self.import_course()
        point_list = [course_point.pos for course_point in self.course_points]
        
        ## the following steps will allow our formula to reference surrounding points
        #add last point to front of list
        point_list.insert(0,point_list[len(point_list)-1])
        
        #take oringinal starting point and add it to the end
        point_list.append(point_list[1])
        for i, point in enumerate(point_list):
            if i==0 or i==len(point_list)-1: continue
            else:
                point1 = point_list[i-1]
                print(i-1,' ',point1)
                point2 = point
                print(i,' ',point2)
                point3 = point_list[i+1]
                print(i+1,' ',point3)
#                
#                point1_2_dist = distance_between(point1,point2)
#                point1_3_dist_halved = distance_between(point1,point3)/2 
                
                point1_from_origin2 = tuple(map(operator.sub,point1,point2))
                point3_from_origin2 = tuple(map(operator.sub,point3,point2))
                angle_to_point1 = math.atan2(*point1_from_origin2)#-math.pi/2
                angle_to_point3 = math.atan2(*point3_from_origin2)#-math.pi/2
                angles_list = [angle_to_point1,angle_to_point3]
                point2_radians = sum(angles_list)/len(angles_list)
                point2_radians_inverse = point2_radians+math.pi

                self.outer_verticies.append(add_pos(new_pos(point2_radians, self.course_width/2),point ) )
                self.inner_verticies.append(add_pos(new_pos(point2_radians_inverse, self.course_width/2),point ) )
                
#        #check if lines intersect, if so, flip vertices
#        vertices_len = len(self.outer_verticies)
#        for i in range(vertices_len):
#            next_i = i+1
#            if next_i>vertices_len: next_i=0
#            outer_point1, inner_point_1 = self.outer_verticies[i],self.inner_verticies[i]
#            outer_point2, inner_point_2 = self.outer_verticies[next_i],self.inner_verticies[next_i]
#            line = LineString([(bike_start),(bike_end)]) #LineString([(0, 0), (1, 1)])
#            other = LineString([(start_point),(end_point)]) #LineString([(0, 1), (1, 0)])
#            
#            
#            if line.intersects(other):
#                pass
                
    def draw_created_course(self):
        [pygame.draw.circle(self.gameDisplay, (255, 255, 255), course_point.pos,int(course_point.radius) ) for course_point in self.course_points]
        
    def update_course_creator(self,click,mouse_pos):
        self.create_course_points(click,mouse_pos)
        self.draw_created_course()

    def draw_game(self):
        pygame.draw.lines(self.gameDisplay, (255, 255, 255), False, self.outer_verticies)
        pygame.draw.lines(self.gameDisplay, (255, 255, 255), False, self.inner_verticies)
        
    def update_game(self):
        self.draw_game()





