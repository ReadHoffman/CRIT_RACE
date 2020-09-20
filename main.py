# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 17:47:41 2020

@author: Read
"""

from __future__ import print_function
import os
os.environ["PATH"] += os.pathsep + 'C:/Users/Read/Miniconda3/Library/bin/graphviz/'
import neat
import pygame
#import math
#import random
#import time
#import operator
#from nnet import Nnet
from defs import *
from course import Course
from bike import Bike, BikeCollection
#from shapely.geometry import LineString
from IPython.core.display import HTML



def loop_game(genomes,config):
    gameDisplay = pygame.display.set_mode((DISPLAY_W,DISPLAY_H))
    pygame.display.set_caption('CRIT RACE')

    running = True
    
    course = Course(gameDisplay)
    course.import_course()

    label_font = pygame.font.SysFont("arial", DATA_FONT_SIZE)

    clock = pygame.time.Clock()
    dt = 0
    game_time = 0
    frame = 0
    global num_iterations
    num_iterations += 1
    
    
    #creates collection of bike instances and population of neural nets
#    bikes = BikeCollection(gameDisplay,course)
    
    bikes = []
    # assign genomes
    i=0
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        bikes.append(Bike(gameDisplay,course ) )
        bikes[i].genome = genome
        bikes[i].genome_id = genome_id
        bikes[i].nnet = net
        i+=1

        
    while running:
        dt = clock.tick(FPS)
        game_time += dt
        gameDisplay.fill(BLACK)
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                running = False
                pygame.display.quit
                pygame.quit()
                break
    
        course.update_game()
        
        num_alive = 0
        for bike in bikes:
            bike.update(course,game_time,frame)
            if bike.alive == True:
                num_alive += 1
        
#        num_alive = bikes.update(course,game_time)
    
        if num_alive == 0:
            game_time = 0
#            print("Fitness")
            i=0
            for genome_id, genome in genomes:
#                fitness = [ bike.fitness for bike in bikes if genome_id==bike.genome_id][0]
#                if fitness is None:
#                    print("bike.fitness is none. Error.  Overriding to 0. ")
#                    fitness = 0
                genome.fitness = bikes[i].fitness 
                i+=1
            generation_fitness_max = max([x.fitness for x in bikes])
            print("Max Fitness: ",generation_fitness_max)
                


            [bike.reset() for bike in bikes]
            running=False
    
        update_data_labels(gameDisplay, dt, game_time, num_iterations, num_alive, label_font)
        pygame.display.update()
        frame+=1
        
    
    


def run_game(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)
    
    pygame.init()
 
    p = neat.Population(config) 

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1000))
    
    winner = p.run(loop_game)
    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))
    
    
    pygame.display.quit
    pygame.quit()



if __name__== "__main__":
  
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    print(config_path)
#    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
#                         neat.DefaultSpeciesSet, neat.DefaultStagnation,config_path)
    run_game(config_path)
    
    
