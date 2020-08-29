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
import numpy as np



class Bike:
    def __init__(self,gameDisplay,course):
        self.gameDisplay = gameDisplay
        self.course = course
        self.color = BIKE_COLOR
        self.highlight = BIKE_HIGHLIGHT
        self.radius = BIKE_WIDTH
        self.pos = add_pos(course.course_points[1].pos,(-BIKE_STARTING_OFFSET_X,course.course_width*.1))
        self.pos_start = self.pos
        self.vector = (0,0)
        self.speed = 0
        self.radians_heading = 0
        self.commands = [0,0]
        self.nnet = Nnet(NNET_INPUTS, NNET_HIDDEN, NNET_OUTPUTS)
        self.dist_ahead = 0
        self.dist_right = 0
        self.dist_left = 0
        self.dist_ahead_right = 0
        self.dist_ahead_left = 0
        self.dist_back = 0
        self.alive = True
        self.fitness = 0
        self.fitness_relativity = 0
        self.time_lived = 0
        self.progress_line_max = 0
        self.time_last_progress_line_achieved = 0
        self.progress_window_min = 0
        self.progress_window_max = 0
        self.lap = 0
        self.assessment_group = "Bad"
        
        #vision
        self.wall_intersect_points = [(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)] #ahead, right, left, ahead-right, ahead-left, back
        self.vision_radian_delta = [0,-math.pi/2,math.pi/2,-math.pi/4,math.pi/4,math.pi]

    def heading_gap_to_next_waypoint(self,course):
        # for model input
        next_waypoint = course.course_points[self.progress_line_max+1].pos
        vector = tuple(map(operator.sub,self.pos,next_waypoint  ))
        return abs(math.atan2(*vector)-self.radians_heading)

    def reset(self):
        self.alive = True
        self.speed = 0
        self.fitness = 0
        self.time_lived = 0
        self.pos = self.pos_start
        self.color = BIKE_COLOR
        self.progress_line_max = 0
        self.time_last_progress_line_achieved = 0
        self.time_lived = 0
        self.radians_heading = 0
        self.commands = [0,0]
        
    def update_progress(self,course,game_time):
#        if line intersects with progress line, get the progress line's index and that is the max score
        prior_max_progress_line = self.progress_line_max
        course_len = len(course.progress_lines)-1
        line1 = self.bike_line()
        for i,line2 in enumerate(course.progress_lines):
            if lines_intersect_bool(line1[0], line1[1], line2[0], line2[1]):
                if i==self.progress_line_max+1:
                    self.progress_line_max = i
                    self.time_last_progress_line_achieved = game_time
                    if prior_max_progress_line == course_len and self.progress_line_max == 0:
                        self.lap +=1
                        
                lag_i = i-1
                lead_i = i+1
                if i == 0:
                    lag_i = course_len
                if i == course_len:
                    lead_i = 0
                self.progress_window_min = lag_i
                self.progress_window_max = lead_i
                    
    def update_fitness(self,course):
        fit_lap = self.lap*len(course.progress_lines)
        fit_waypoint_progress = self.progress_line_max+1
        fit_dist_to_waypoint = distance_between(self.pos,course.course_points[self.progress_line_max+1].pos)/DISPLAY_W
        fit_heading = (self.heading_gap_to_next_waypoint(course)/(math.pi*100))
        self.fitness = fit_lap+fit_waypoint_progress-fit_dist_to_waypoint-fit_heading
    
    def bike_line(self):
        start_pos = add_pos(new_pos(self.radians_heading,self.radius),self.pos)
        end_pos = add_pos(new_pos(self.radians_heading+math.pi,self.radius),self.pos)
        return (start_pos,end_pos)
    
    def get_vision_intersection_point(self,course,game_time):
        vision_points = self.wall_intersect_points
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
            
            if len(intersections_dist)>0:
                min_dist = min(intersections_dist) 
                min_indices = [k for k, intersection_dist in enumerate(intersections_dist) if intersection_dist == min_dist] 
                
                vision_points[j] = intersections[min(min_indices)]
                vision_distances[j] = intersections_dist[min(min_indices)]
            else:
                vision_points[j] = line1_start
                vision_distances[j] = 0
            
    
    def draw(self):
#        pygame.draw.circle(self.gameDisplay, self.color, (int(self.pos[0]),int(self.pos[1])), self.radius) #removed for speed
        start_pos, end_pos = self.bike_line()
        pygame.draw.line(self.gameDisplay, self.highlight, start_pos, end_pos, BIKE_HEADING_WIDTH)
        
#        bike_leading_point = self.bike_line()[0]
#        [pygame.draw.line(self.gameDisplay, VISION_COLOR, bike_leading_point, wall_intersect_point, VISION_WIDTH) for wall_intersect_point in self.wall_intersect_points]
        
        
    def update(self,course,game_time):
        self.draw()
#        self.get_vision_intersection_point(course,game_time)
        self.update_vector(course)
        self.update_progress(course,game_time)
        self.check_collision(course,game_time)
        self.update_pos()
        
    
    def update_vector(self,course):
        if self.alive:
            max_dist = distance_between((DISPLAY_W,DISPLAY_H),(0,0))
            inputs_list = [self.dist_ahead, self.dist_right, self.dist_left, self.dist_ahead_right, self.dist_ahead_left, self.dist_back,self.heading_gap_to_next_waypoint(course)]
            inputs_list_denominator = [DISPLAY_W, COURSE_WIDTH/2, COURSE_WIDTH/2, COURSE_WIDTH, COURSE_WIDTH, DISPLAY_W,math.pi*2]
            model_inputs = [inputs/inputs_list_denominator[i] for i, inputs in enumerate(inputs_list)]
            nnet_output = self.nnet.get_outputs(model_inputs)
            for i in range(len(self.commands)):
                self.commands[i] = nnet_output[i]

            if self.commands[0]>=COMMAND_CHANCE_FORWARD : self.speed += BIKE_ACCELERATION 
            if self.commands[0]<=COMMAND_CHANCE_SLOW: self.speed = max([self.speed-BIKE_DECELERATION,0])
            if self.commands[1]>=COMMAND_CHANCE_TURN_RIGHT: self.radians_heading -= BIKE_TURN_INCREMENT
            if self.commands[1]<=COMMAND_CHANCE_TURN_LEFT: self.radians_heading += BIKE_TURN_INCREMENT
            self.vector = new_pos(self.radians_heading,self.speed)

    def update_pos(self):
        if self.alive:
            self.pos = tuple(map(operator.add, self.pos, self.vector))
    
    def check_collision(self,course,game_time):
        course_vertices_list = [course.inner_verticies,course.outer_verticies]
        
#        for course_vertices in course_vertices_list:
#            course_vertices_len = len(course_vertices)
#            
#            for i, course_line in enumerate(course_vertices): 
#                start_point = course_line
#                if i+1==course_vertices_len: end_point = course_vertices[0]
#                else: end_point = course_vertices[i+1]
#                
#                bike_start,bike_end = self.bike_line()
#                
#                line = LineString([(bike_start),(bike_end)]) #LineString([(0, 0), (1, 1)])
#                other = LineString([(start_point),(end_point)]) #LineString([(0, 1), (1, 0)])
#                
#                
#                if line.intersects(other) or game_time-self.time_last_progress_line_achieved>REQUIRED_PROGRESS:
##                    print("Crash")
#                    self.speed = 0
#                    self.vector = (0,0)
#                    self.alive = False
#                    self.color = (0,255,0) #test
#                    self.update_fitness(course)

    def check_collision(self,course,game_time):
        course_lines_list = [course.inner_lines,course.outer_lines]
        
        for course_lines in course_lines_list:            
            for i, course_line in enumerate(course_lines)  :
                if i==self.progress_window_min or i==self.progress_window_max-1:                 
                    bike_start,bike_end = self.bike_line()
                    
                    line = LineString([(bike_start),(bike_end)]) #LineString([(0, 0), (1, 1)])
                    other = LineString([*course_line]) #LineString([(0, 1), (1, 0)])
                    
                    
                    if line.intersects(other) or game_time-self.time_last_progress_line_achieved>REQUIRED_PROGRESS:
    #                    print("Crash")
                        self.speed = 0
                        self.vector = (0,0)
                        self.alive = False
                        self.color = (0,255,0) #test
                        self.update_fitness(course)

    def create_offspring(p1, p2, gameDisplay,course):
        new_bike = Bike(gameDisplay,course)
        new_bike.nnet.create_mixed_weights(p1.nnet, p2.nnet)
        return new_bike
    
    
class BikeCollection:

    def __init__(self, gameDisplay,course):
        self.gameDisplay = gameDisplay
        self.bikes = []
        self.create_new_generation(course)

    def create_new_generation(self,course):
        self.bikes = []
        for i in range(0, GENERATION_SIZE):
            self.bikes.append(Bike(self.gameDisplay,course ) )

    def update(self, course,game_time):
        num_alive = 0
        for bike in self.bikes:
            bike.update(course,game_time)
            if bike.alive == True:
                num_alive += 1

        return num_alive

    def evolve_population(self,course):

#        for bike in self.bikes:
#            # update fitness
#            bike.fitness += bike.time_lived * PIPE_SPEED

        #sort list to find the most fit
        self.bikes.sort(key=lambda x: x.fitness, reverse=True)
        
        bikes_fitness = [bike.fitness for bike in self.bikes]
        print("Fitness Results: ")
        [print(bike.fitness) for bike in self.bikes]
        bikes_fitness_min = min(bikes_fitness)
        bikes_fitness_max = max(bikes_fitness)
        bikes_fitness_abs_range = bikes_fitness_max-bikes_fitness_min
        for bike in self.bikes:
            bike.fitness_relativity = (bike.fitness-bikes_fitness_min)/(bikes_fitness_abs_range+.0001) #.001 to avoid dividing by zero

        cut_off = int(len(self.bikes) * MUTATION_CUT_OFF) #cutoff is .4 right now
        good_bikes = self.bikes[0:cut_off]
#        good_fitness_min = min([bike.fitness for bike in self.bikes[0:cut_off]])
#        for bike in self.bikes:
#            if bike.fitness >=good_fitness_min:
#                bike.assessment_group = "Good"
                
#        bad_bikes = self.bikes[cut_off:]
#        num_bad_to_take = int(len(self.bikes) * MUTATION_BAD_TO_KEEP) #cutoff is .2 right now
#
#        for bike in bad_bikes:
#            bike.nnet.modify_weights(1-MUTATION_PCT_WEIGHTS_TO_CHANGE)
#
        new_bikes = []
#
#        idx_bad_to_take = np.random.choice(np.arange(len(bad_bikes)), num_bad_to_take, replace=False)
#
#        for index in idx_bad_to_take:
#            new_bikes.append(bad_bikes[index])

        new_bikes.extend(good_bikes)

#        children_needed = len(self.bikes) - len(new_bikes)

#        while len(new_bikes) < len(self.bikes):
#            idx_to_breed = np.random.choice(np.arange(len(good_bikes)), 2, replace=False)
#            if idx_to_breed[0] != idx_to_breed[1]:
#                parent_list = [good_bikes[idx_to_breed[1]] , good_bikes[idx_to_breed[0]] ]
#                new_bike = Bike.create_offspring(parent_list[0], parent_list[1], self.gameDisplay,course)
#                offspring_fitness_relativity_avg = sum([x.fitness_relativity for x in parent_list]) / len(parent_list)
#                if random.random() < MUTATION_MODIFY_CHANCE_LIMIT: #.4
#                    print("Offspring relativity avg:",offspring_fitness_relativity_avg," % weights changed:",1-offspring_fitness_relativity_avg*MUTATION_WEIGHT_MODIFY_FACTOR)
#                    new_bike.nnet.modify_weights(offspring_fitness_relativity_avg*MUTATION_WEIGHT_MODIFY_FACTOR) 
#                new_bikes.append(new_bike)

        while len(new_bikes) < len(self.bikes):
            new_bike = Bike.create_offspring(self.bikes[0], self.bikes[0], self.gameDisplay,course)
            new_bike.nnet.modify_weights(MUTATION_PCT_WEIGHTS_TO_CHANGE) 
            new_bikes.append(new_bike)



        for bike in new_bikes:
            bike.reset();

        self.bikes = new_bikes