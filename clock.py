#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""
Clock
- analog clock

2023-05-08 - v 1.0.0
- initial version

ESC = exit

"""

import sys
import datetime
import os
import yaml
import math
import pygame
from pygame.locals import *
from common import *

VERSION = "1.0.0"

CZ = 3 * math.pi / 4
pi2 = math.pi * 2


def rotate(r, size, px, py):
    """rotate around point (px, py)"""
    r0 = r - CZ
    x = math.cos(r0) * size - math.sin(r0) * size + px
    y = math.sin(r0) * size + math.cos(r0) * size + py

    x = int(x)
    y = int(y)

    return x,y



def init_screen(full_screen_flag):
    """initalize screen"""
    pygame.init()

    # full screen
    if full_screen_flag:
        infoObject = pygame.display.Info()
        #print("screen %s x %s" % (infoObject.current_w, infoObject.current_h))
        screen_x = infoObject.current_w
        screen_y = infoObject.current_h
    
        screen = pygame.display.set_mode((screen_x, screen_y), FULLSCREEN)
    else:
        screen_x = config.get("screen", {}).get("window_x", 256)
        screen_y = config.get("screen", {}).get("window_y", 191)
        
        screen = pygame.display.set_mode((screen_x, screen_y), HWSURFACE|HWPALETTE, 8)
    
    pygame.display.set_caption("Background")

    pygame.mouse.set_visible(False)
    
    pygame.display.set_allow_screensaver(False)

    return screen, screen_x, screen_y




def background(screen, screen_x, screen_y):
    """main program"""

    clock_tick = 50
    clock = pygame.time.Clock()

    bg = pygame.Surface(screen.get_size())
    bg = bg.convert()
   
    # screen center    
    cx = screen_x // 2
    cy = screen_y // 2
    

    # clock settings

    r1 = 0.1 # how wide is each hand
    l1 = 0.35 # where the widest point in the hand


    clock_config = config.get("clock", {})
    second_flag = False
    if clock_config.get("show_second_hand", False):
        second_flag = True
    
    lw = 1
    if clock_config.get("solid_fill", False):
        lw = 0

    background_color = convert_color(clock_config.get("background_color", "#000000"))
    second_hand_color = convert_color(clock_config.get("second_hand_color", "#FFFFFF"))

    minute_hand_color = convert_color(clock_config.get("minute_hand_color", "#FFFFFF"))
    hour_hand_color = convert_color(clock_config.get("hour_hand_color", "#FFFFFF"))
    
    hour_dot_color = convert_color(clock_config.get("hour_dot_color", "#FFFFFF"))
    minute_dot_color = convert_color(clock_config.get("minute_dot_color", "#FFFFFF"))

    last_sec = -1

    redraw_flag = True
    draw_clock_face_flag = True
    done = False


    while not done:

        now = datetime.datetime.now()

        # comment out for ticks on seconds only
        redraw_flag = True

        if now.second != last_sec:
            last_sec = now.second

            redraw_flag = True

        if draw_clock_face_flag:
            bg.fill(background_color)

            # draw hours, minutes
            # copy to background
            r = 0
            for s in range(0,60):
                r = r + (1 / 60.0) * pi2
                x, y = rotate(r, 225, cx, cy)
                pygame.draw.circle(bg, minute_dot_color, (x, y), 5, 0)

            r = 0
            for s in range(0,12):
                r = r + (1 / 12.0) * pi2
                x, y = rotate(r, 225, cx, cy)
                pygame.draw.circle(bg, hour_dot_color, (x, y), 10, 0)

            bg0 = bg.copy()
            draw_clock_face_flag = False


        if redraw_flag:

            #screen.blit(bg0, (0, 0))
            bg.blit(bg0, (0,0))

            hr = now.hour
            if hr > 12:
                hr = hr - 12
            hr = ((hr + now.minute / 60.0 + now.second / 3600.0) / 12.0 ) * pi2
            
            x, y = rotate(hr, 150, cx, cy)
            x1, y1 = rotate(hr+r1, int(150 * l1), cx, cy)
            x2, y2 = rotate(hr-r1, int(150 * l1), cx, cy)
            pygame.draw.polygon(bg, hour_hand_color, [[cx,cy], [x1,y1], [x,y], [x2,y2]], lw)

            # minutes
            m = ((now.minute + now.second / 60.0) / 60.0 ) * pi2
            x, y = rotate(m, 200, cx, cy)
            x1, y1 = rotate(m+r1, int(200*l1), cx, cy)
            x2, y2 = rotate(m-r1, int(200*l1), cx, cy)
            pygame.draw.polygon(bg, minute_hand_color, [[cx,cy], [x1,y1], [x,y], [x2,y2]], lw)
            

            # seconds
            if second_flag:
                s = ((now.second + now.microsecond/1000000.0) / 60.0) * pi2
                x, y = rotate(s, 250, cx, cy)
                x1, y1 = rotate(s+r1, int(250*l1), cx, cy)
                x2, y2 = rotate(s-r1, int(250*l1), cx, cy)
                pygame.draw.polygon(bg, second_hand_color, [[cx,cy], [x1,y1], [x,y], [x2,y2]], lw)

            xx = yy = 0
            # screen shake
            #xx = random.choice([0,5,10,15,20])
            #yy = random.choice([0,5,10,15,20])
            screen.blit(bg, (xx, yy))
            pygame.display.flip()
            
            redraw_flag = False



        clock.tick(clock_tick) 

        for event in pygame.event.get():
            if event.type == QUIT:
                done = True
            elif event.type == KEYDOWN:

                if event.key == K_ESCAPE:
                    done = True            


if __name__ == '__main__':

    # reduce error traceback
    sys.tracebacklimit = 0


    config_file = "config.yaml"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    print("Loading config: {}".format(config_file))
    

    if not os.path.isfile(config_file):
        print("Cannot find config: {}".format(config_file))
        sys.exit(1)
    
    with open(config_file, "r", encoding="utf-8") as fh:
        try:
            config = yaml.load(fh, Loader=yaml.FullLoader)
        except yaml.scanner.ScannerError as err: 
            print("Config file error: {}".format(err))
            sys.exit(1)

    # full screen option
    screen, screen_x, screen_y = init_screen(config.get("screen", {}).get("full_screen", False))

    background(screen, screen_x, screen_y)

    pygame.quit()
    
    sys.exit(0)

