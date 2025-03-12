#!/usr/bin/env python
#! -*- coding: utf-8 -*-

#import pygame

class TxtImg():
    
    # defaults
    shadow_color = (0,0,0)
    text_color = (255,255,255)
    location = "" #bottom-left"
    shadow_offset = 15
    text_padding = 10
    text_str = ""
    
    def __init__(self, text_font, bg, screen_x, screen_y):
        self.text_str = "" 
        self.text_font = text_font
        self.bg = bg
        self.screen_x = screen_x
        self.screen_y = screen_y


    def render_text_shadow(self):

        txt_img = self.text_font.render(self.text_str, 1, self.shadow_color)
        text_xy = txt_img.get_rect()

        # top right
        txt_x = self.text_padding + self.shadow_offset
        txt_y = self.text_padding + self.shadow_offset

        if self.location == "bottom-left":
            txt_x = self.screen_x - text_xy[2] + self.shadow_offset - self.text_padding
            txt_y = self.screen_y - text_xy[3] + self.shadow_offset - self.text_padding
        
        self.bg.blit(txt_img, (txt_x, txt_y))

    def render_text(self):
        txt_img = self.text_font.render(self.text_str, 1, self.text_color)
        text_xy = txt_img.get_rect()
        
        # top right
        txt_x = self.text_padding
        txt_y = self.text_padding

        if self.location == "bottom-left":
            txt_x = self.screen_x - text_xy[2] - self.text_padding
            txt_y = self.screen_y - text_xy[3] - self.text_padding
        
        self.bg.blit(txt_img, (txt_x, txt_y))

