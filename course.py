# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 18:36:46 2020

@author: Read
"""
import pygame
from defs import *

class Course:
    def __init__(self,gameDisplay):
        self.gameDisplay = gameDisplay
        self.outer_num = 8
        self.inner_num = 8
        self.outer_verticies = [(DISPLAY_W*1/10,DISPLAY_H*1/10),(DISPLAY_W*9/10,DISPLAY_H*1/10),(DISPLAY_W*9/10,DISPLAY_H*9/10),(DISPLAY_W*1/10,DISPLAY_H*9/10),(DISPLAY_W*1/10,DISPLAY_H*1/10)]
        self.inner_verticies = [(DISPLAY_W*3/10,DISPLAY_H*3/10),(DISPLAY_W*7/10,DISPLAY_H*3/10),(DISPLAY_W*7/10,DISPLAY_H*7/10),(DISPLAY_W*3/10,DISPLAY_H*7/10),(DISPLAY_W*3/10,DISPLAY_H*3/10)]
    
    def create():
        pass
    
    def draw(self):
        pygame.draw.lines(self.gameDisplay, (255, 255, 255), False, self.outer_verticies)
        pygame.draw.lines(self.gameDisplay, (255, 255, 255), False, self.inner_verticies)
        
    def update(self):
        self.draw()
