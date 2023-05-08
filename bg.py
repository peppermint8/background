#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""
Background screensaver
- rotate through images in a folder, not subfolders
- show weather, stock prices, computer info, time

To do:
- long text scrolling


2023-05-08 - v 1.0.0

keys:
X = next text 
SPACE = next image
ESC = exit

"""

import sys
import datetime
import os
import yaml
#import glob
import random
import pygame
from pygame.locals import *
from common import *

from stock import Stock
from weather import Weather
from text_img import TxtImg

VERSION = "1.0.0"




def get_img_list(collection):
    """get the files in the path"""
    img_path = config.get(collection, {}).get("path")

    # use default (F1) if the path doesn't exist
    if not img_path:
        img_path = config.get("F1", {}).get("path")

    #img_list = glob.glob(os.path.join(img_path))

    img_list = []
    for root, dirs, files in os.walk(os.path.dirname(img_path)):
        for img in files:
            img_list.append(os.path.join(root, img))

    if not img_list:
        collection = "F1"
        img_list = get_img_list(collection) 

    print("{}: {}, images: {}".format(collection, config.get(collection, {}).get("name"), len(img_list)))

    return img_list



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

    clock_tick = 15
    clock = pygame.time.Clock()

    bg = pygame.Surface(screen.get_size())
    bg = bg.convert()

    background_color = convert_color(config.get("screen", {}).get("background_color"))

    bg_font = pygame.font.Font(config.get("text", {}).get("bg_font"),
                               config.get("text", {}).get("bg_font_size"))

    text_color = convert_color(config.get("text", {}).get("color", "#FFFFFF"))
    text_shadow_color = convert_color(config.get("text", {}).get("bg_color", "#000000"))
    text_shadow_offset = config.get("text", {}).get("bg_offset", 48)
    text_padding = config.get("text", {}).get("padding", 25)
    last_sec = -1




    # get random image from the list
    collection = "F1"
    img_list = get_img_list(collection)
    
    
    datetime_format = config.get("date", {}).get("datetime_format", "%H:%M")
    datetime_str = last_datetime_str = ""

    time_obj = TxtImg(bg_font, bg, screen_x, screen_y)
    time_obj.shadow_color = text_shadow_color
    time_obj.shadow_offset = text_shadow_offset
    time_obj.padding = text_padding
    time_obj.text_color = text_color 
    time_obj.text_str = ""
    time_obj.location = config.get("date", {}).get("location", "") 

    now = datetime.datetime.now()


    # random text for top of screen
    text_json = {} # key = string
    text_max_sec = config.get("text_interval_sec", 30)
    text_sec = now.timestamp() + text_max_sec
    text_obj = TxtImg(bg_font, bg, screen_x, screen_y)
    text_obj.shadow_color = text_shadow_color
    text_obj.shadow_offset = text_shadow_offset
    text_obj.padding = text_padding
    text_obj.text_color = text_color 
    text_obj.location = config.get("text_msg_location", "")
    text_obj.text_str = ""
    
    weather_list = []
    weather_api_key = config.get("weather_api_key")
    if weather_api_key:
        for w in config.get("weather_list"):
            if w.get("location"):
                wx = Weather(w.get("location"), weather_api_key)
                wx.update()
                print("- weather: {}".format(wx))
                text_json[wx.zipcode] = str(wx)
                weather_list.append(wx)

        
    weather_max_sec = config.get("weather_interval_sec", 600)
    weather_sec = now.timestamp() + weather_max_sec   

    stock_list = []
    for s in config.get("stock_list"):
        #print(s.get("symbol"), s.get("name"))
        sx = Stock(s.get("symbol"), s.get("name", "unknown"))
        sx.update()
        print("- stock: {}".format(sx))
        text_json[sx.symbol] = str(sx)
        stock_list.append(sx)


    stock_max_sec = config.get("stock_interval_sec", 30)
    stock_sec = now.timestamp() + stock_max_sec    
    stock_open_hr = 13 - 8
    stock_close_hr = 13

    # long test - works
    #text_json['x'] = """Not dead which eternal lie, Stranger eons death may die. Drain you of your sanity. Face the thing that should not be!"""


    txt_key_list = list(text_json.keys())
    #txt_key = random.choice(txt_key_list)
    txt_cnt = 0
    txt_key = txt_key_list[txt_cnt]
    text_obj.text_str = text_json[txt_key]

    # how many seconds before getting a new image
    screen_max_sec = config.get("screen_interval_sec", 30)
    screen_sec = now.timestamp() + screen_max_sec
    fade_speed = config.get("background_fade_speed", 5)
    fade_in = 255

    old_img = None
    my_img = None

    new_img_flag = True
    redraw_flag = True
    done = False


    while not done:
            

        now = datetime.datetime.now()

        if fade_in <= 255 and fade_speed > 0:
            fade_in += fade_speed
            fade_in = min(fade_in, 255)
            redraw_flag = True

        # time to switch images?
        if now.timestamp() >= screen_sec:
            new_img_flag = True
        
        if now.timestamp() >= stock_sec:

            if now.weekday() < 5 and stock_open_hr <= now.hour <= stock_close_hr:
                print("Stock market updating ...")
                for s in stock_list:
                    s.update()
                    text_json[s.symbol] = str(s)
                    #print("- {}".format(s))

        if now.timestamp() >= weather_sec:
            weather_sec = now.timestamp() + weather_max_sec   
            for w in weather_list:
                w.update()
                text_json[w.zipcode] = str(w)

        # new ticker value
        if now.timestamp() >= text_sec:
            txt_cnt += 1
            if txt_cnt > len(txt_key_list) - 1:
                txt_cnt = 0
            text_sec = now.timestamp() + text_max_sec
            text_obj.text_str = ""
            #txt_key = random.choice(txt_key_list)
            txt_key = txt_key_list[txt_cnt]
            text_obj.text_str = text_json[txt_key]
            redraw_flag = True



        if now.second != last_sec:
            last_sec = now.second

            now = datetime.datetime.now()
            datetime_str = now.strftime(datetime_format)
            time_obj.text_str = datetime_str
            if last_datetime_str != datetime_str:
                redraw_flag = True



        if new_img_flag:
            screen_sec = now.timestamp() + screen_max_sec
            the_img = random.choice(img_list)
            if test_img(the_img):

                
                if my_img:
                    old_img = my_img
                    old_img_x = img_x
                    old_img_y = img_y
                    # store old_img_x & y
                my_img, img_x, img_y = scale_image(the_img, screen_x, screen_y)
                
                # reset new image timer
                new_img_flag = False
                redraw_flag = True
                if fade_speed > 0:
                    fade_in = 0
            else:
                print("- {} is not a file".format(the_img))
        
        if redraw_flag:

            bg.fill(background_color)
            
            if old_img and fade_speed > 0:
                old_img.set_alpha(255 - fade_in)
                bg.blit(old_img, (old_img_x, old_img_y))

            if fade_in <= 255:
                my_img.set_alpha(fade_in)
            
            bg.blit(my_img, (img_x, img_y))
            

            # time textbox
            time_obj.render_text_shadow()
            time_obj.render_text()

            # stock, weather, etc
            text_obj.render_text_shadow()
            text_obj.render_text()
  

            screen.blit(bg, (0, 0))
            pygame.display.flip()
            #bg0 = bg.copy()
            
            redraw_flag = False



        clock.tick(clock_tick) 

        for event in pygame.event.get():
            if event.type == QUIT:
                done = True
            elif event.type == KEYDOWN:

                if event.key == K_ESCAPE:
                    done = True            

                if event.key == K_x:
                    text_sec = 0
                    redraw_flag = True

                if event.key == K_SPACE:
                    new_img_flag = True

        all_keys = pygame.key.get_pressed()
        if all_keys[pygame.K_F1] and all_keys[pygame.K_LSHIFT]:
            img_list = get_img_list("F1")
            new_img_flag = True
        if all_keys[pygame.K_F2] and all_keys[pygame.K_LSHIFT]:
            img_list = get_img_list("F2")
            new_img_flag = True
        if all_keys[pygame.K_F3] and all_keys[pygame.K_LSHIFT]:
            img_list = get_img_list("F3")
            new_img_flag = True
        if all_keys[pygame.K_F4] and all_keys[pygame.K_LSHIFT]:
            img_list = get_img_list("F4")
            new_img_flag = True
        if all_keys[pygame.K_F5] and all_keys[pygame.K_LSHIFT]:
            img_list = get_img_list("F5")
            new_img_flag = True                                    



if __name__ == '__main__':

    # reduce error traceback
    #sys.tracebacklimit = 0


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

