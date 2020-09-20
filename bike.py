# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 19:42:30 2020

@author: Read
"""
#import random
import math
import pygame
import operator
from defs import *
from nnet import Nnet
from course import Course #test
#import shapely
#from shapely.geometry import LineString, Point
#import numpy as np



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
        self.speed = 4
        self.radians_heading = 0
        self.nnet = Nnet(NNET_INPUTS, NNET_HIDDEN, NNET_OUTPUTS)
        self.dist_ahead = 0
        self.dist_right = 0
        self.dist_left = 0
        self.dist_ahead_right = 0
        self.dist_ahead_left = 0
        self.dist_back = 0
        self.alive = True
        self.fitness = 0
        self.frames_alive = 0
        self.fitness_relativity = 0
        self.time_lived = 0
        self.progress_line_max = 0
        self.progress_line_prior = 0
        self.time_last_progress_line_achieved = 0
        self.progress_window_min = 0
        self.progress_window_max = 0
        self.lap = 0
        self.assessment_group = "Bad"
        
        self.genome = None
        self.genome_id = None
        self.species = None
        
        #vision
        self.vision_end_points = [(0,0),(0,0)]#,(0,0),(0,0),(0,0)] #ahead, right, left, ahead-right, ahead-left
#        self.vision_radian_delta = [0,-math.pi/2,math.pi/2,-math.pi/4,math.pi/4]
        self.vision_radian_delta = [-math.pi/4,math.pi/4]

    def next_waypoint(self,course):
        course_points_len = len(course.course_points)
        if self.progress_line_max+1== course_points_len:
            result = course.course_points[0].pos
        else:
            result = course.course_points[self.progress_line_max+1].pos
        return result

    def heading_gap_to_next_waypoint(self,course):
        # for model input
        next_waypoint = self.next_waypoint(course)
        vector = tuple(map(operator.sub,self.pos,next_waypoint  ))
        heading = self.radians_heading - math.atan2(*vector)
        
        gap = distance_between(self.pos,next_waypoint)
        return (heading,gap)

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
        
    def update_progress(self,course,game_time):
#        if line intersects with progress line, get the progress line's index and that is the max score
        prior_max_progress_line = self.progress_line_max
        course_index_max = len(course.progress_lines)-1
        line1 = self.bike_line()
        #for every course progress line
        for i,line2 in enumerate(course.progress_lines):
            #for nearby lines only
            if i==self.progress_window_min or i==self.progress_window_min+1 or i ==self.progress_window_max or i ==self.progress_window_max+1:
                #if the bike intersects with it
                if lines_intersect_bool(line1[0], line1[1], line2[0], line2[1]):  
                    #if the intersected progress line is 1 more than the prior max...             
                    if i==prior_max_progress_line+1:
                        #then set the progress max to the intersected progress line
                        self.progress_line_max = i
                        #and reset the progress timer
                        self.time_last_progress_line_achieved = game_time
                        #if looping around to the start...
                        if prior_max_progress_line == course_index_max and self.progress_line_max == 0:
                            #increment the lap counter up
                            self.lap +=1
                    
                    #going backwards is bad
                    if (prior_max_progress_line==0 and i==course_index_max) or i<= prior_max_progress_line-1:
                        self.crash_bike(course)
                    
                    #set progress window
                    lag_i = i-1
                    lead_i = i+1
                    if i == 0:
                        lag_i = course_index_max
                    if i == course_index_max:
                        lead_i = 0
                    self.progress_window_min = lag_i
                    self.progress_window_max = lead_i
              


                    
    def update_fitness(self,course):
        if self.alive==True: self.frames_alive +=.5
        fit_lap = self.lap*len(course.progress_lines)*1000
        fit_waypoint_progress = (self.progress_line_max+1)*100
        fit_dist_to_waypoint = distance_between(self.pos,self.next_waypoint(course) )/DISPLAY_W *100
#        fit_heading = abs(self.heading_gap_to_next_waypoint(course)/(math.pi))
        self.fitness = fit_lap+fit_waypoint_progress-fit_dist_to_waypoint+self.frames_alive#-fit_heading
    
    def bike_line(self):
        start_pos = add_pos(new_pos(self.radians_heading,self.radius),self.pos)
        end_pos = add_pos(new_pos(self.radians_heading+math.pi,self.radius),self.pos)
        return (start_pos,end_pos)
    
    def get_vision_intersection_point(self,course,frame):
#       vision_distances = [self.dist_ahead, self.dist_right, self.dist_left, self.dist_ahead_right, self.dist_ahead_left ]
        vision_distances = [self.dist_ahead_right, self.dist_ahead_left ]
        
        for i in range(len(vision_distances)):
            intersections=[]
            line1_start = self.bike_line()[0]
            vision_end_point = new_pos(self.radians_heading+self.vision_radian_delta[i],BIKE_VISION_MAX)
            line1_end = add_pos(vision_end_point,line1_start)

            course_lines_list = [course.outer_lines, course.inner_lines]
            for course_lines in course_lines_list:
                for course_line in course_lines:
                    point1, point2 = course_line
                    #if the line points are outside of max vision range, skip calculating the intersection
                    if distance_between(line1_start,point1)>BIKE_VISION_MAX*3 and distance_between(line1_start,point2)>BIKE_VISION_MAX*3:
                        continue
                    else:
                        intersection= lines_intersect_pos(line1_start, line1_end, point1, point2)
                        if intersection!=None:
                            intersections.append( (intersection,distance_between(line1_start,intersection)) )
                    
            if len(intersections)==0:
                vision_distances[i] = BIKE_VISION_MAX
                self.vision_end_points[i] = line1_end
                continue
            else:
                #find closest by sorting ascending by second element which is distance
                intersections_sorted = Sort_Tuple(intersections) 
                self.vision_end_points[i], vision_distances[i] = intersections_sorted[0]
               
            
    
    def draw(self):
#        pygame.draw.circle(self.gameDisplay, self.color, (int(self.pos[0]),int(self.pos[1])), self.radius) #removed for speed
        start_pos, end_pos = self.bike_line()
        pygame.draw.line(self.gameDisplay, self.highlight, start_pos, end_pos, BIKE_HEADING_WIDTH)
#        [pygame.draw.line(self.gameDisplay, (0,255,0), start_pos, vision_end_point, 1) for vision_end_point in self.vision_end_points]
        
        
        
    def update(self,course,game_time,frame):
        self.draw()
        self.get_vision_intersection_point(course,frame)
        self.update_vector(course)
        self.update_progress(course,game_time)
        self.check_collision(course,game_time)
        self.update_pos()
        
    
    def update_vector(self,course):
        if self.alive:
#            max_dist = distance_between((DISPLAY_W,DISPLAY_H),(0,0))
#            heading, gap = self.heading_gap_to_next_waypoint(course)
            inputs_list = [self.dist_ahead_right, self.dist_ahead_left] #removed dist back 
#            inputs_list = [self.dist_ahead, self.dist_right, self.dist_left, self.dist_ahead_right, self.dist_ahead_left] #removed dist back 
            inputs_list2 = [min( BIKE_VISION_MAX ,input_ ) for input_ in inputs_list ]
#            inputs_list_denominator = [DISPLAY_W/2, COURSE_WIDTH/2, COURSE_WIDTH/2, COURSE_WIDTH, COURSE_WIDTH] #removed dist back denom 
#            inputs_list_denominator = [BIKE_VISION_MAX, BIKE_VISION_MAX, BIKE_VISION_MAX, BIKE_VISION_MAX, BIKE_VISION_MAX] #removed dist back denom 
            model_inputs = [inputs/BIKE_VISION_MAX for i, inputs in enumerate(inputs_list2)]
#            nnet_output = self.nnet.get_outputs(model_inputs)
            nnet_output = self.nnet.activate(model_inputs)
#            print(nnet_output)

#            if commands[0]>=COMMAND_CHANCE_FORWARD : self.speed += BIKE_ACCELERATION 
#            if commands[1]>=COMMAND_CHANCE_TURN_RIGHT: self.radians_heading -= BIKE_TURN_INCREMENT
#            if commands[2]>=COMMAND_CHANCE_TURN_LEFT: self.radians_heading += BIKE_TURN_INCREMENT
#            self.radians_heading -= BIKE_TURN_INCREMENT*commands[1]
#            self.radians_heading += BIKE_TURN_INCREMENT*commands[2]
            self.radians_heading += BIKE_TURN_INCREMENT*nnet_output[0]
            self.radians_heading -= BIKE_TURN_INCREMENT*nnet_output[1]
#            if commands[2]>=COMMAND_CHANCE_SLOW: self.speed -= BIKE_DECELERATION
#            self.speed = self.speed*(1-FRICTION)
            self.vector = new_pos(self.radians_heading,max([self.speed,0]) )

    def update_pos(self):
        if self.alive:
            self.pos = tuple(map(operator.add, self.pos, self.vector))
    
#    def check_collision(self,course,game_time):
#        course_vertices_list = [course.inner_verticies,course.outer_verticies]
#        
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
        
        #for both inside lines and outside lines
        for course_lines in course_lines_list: 
            #for every line on the course
            for i, course_line in enumerate(course_lines)  :
                #only check relevant lines near rider
                if i==self.progress_window_min or i==self.progress_window_min+1 or i==self.progress_window_max-1:                 
                    bike_start,bike_end = self.bike_line()
                    
                    line = LineString([(bike_start),(bike_end)]) #LineString([(0, 0), (1, 1)])
                    other = LineString([*course_line]) #LineString([(0, 1), (1, 0)])
                    
                    
                    if line.intersects(other) or game_time-self.time_last_progress_line_achieved>REQUIRED_PROGRESS:
                        self.crash_bike(course)

    def crash_bike(self,course):
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


    def reset_bikes(self):
        [bike.reset() for bike in self.bikes]


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