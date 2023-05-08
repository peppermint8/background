#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""
Common functions

"""

import os
import sys
import pygame
import random

def get_wh(iw, ih, max_x, max_y):
    """scale image size"""

    new_w = iw 
    new_h = ih
    
    w1 = new_w / max_x
    h1 = new_h / max_y
    
    """
    if iw == 1920 and ih == 1200:
        new_w = max_x
        new_h = max_y
    elif iw == 2560 and ih == 1440:
        new_w = max_x
        new_h = max_y
    elif iw == 2048 and ih == 1163:
        new_w = max_x
        new_h = max_y
    """
    if w1 > h1:
        new_w = new_w // w1
        new_h = new_h // w1
    else:
        new_w = new_w // h1
        new_h = new_h // h1
    
    return new_w, new_h


def convert_color(color_str):
    """convert "#RRGGBB" to pygame color"""
    clr = (0, 0, 0)
    if not color_str:
        return get_rgb()

    if not color_str.startswith("#"):
        color_str = "#" + color_str
    
    clr = pygame.Color(color_str)

    return clr

def test_img(img_file):
    """test if the file 'smells' like an image"""

    test_flag = False

    if os.path.isfile(img_file):
        i = img_file.lower()
        if i.endswith(".jpg") or i.endswith(".png") or i.endswith(".jpeg") or i.endswith(".bmp") or i.endswith(".gif"):
            test_flag = True


    return test_flag                


def scale_image(img, max_x, max_y):

    my_img = None
    img_x = img_y = -1
    try:
        my_img = pygame.image.load(img).convert()
        iw, ih = my_img.get_rect().size
        new_w, new_h = get_wh(iw, ih, max_x, max_y)
        my_img = pygame.transform.scale(my_img, (new_w, new_h))
        # randomly flip horiz
        if random.random() >= 0.5:
            my_img = pygame.transform.flip(my_img, True, False)

        # centering
        img_x = (max_x - new_w) // 2
        img_y = (max_y - new_h) // 2

    except pygame.error as e:
        print("image error: {}".format(e))
        print("image: {}".format(img))

    return my_img, img_x, img_y






if __name__ == '__main__':

    
    sys.exit(0)
