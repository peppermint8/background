#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""
Background screensaver
- rotate through images in a folder, not subfolders
- show weather, stock prices, computer info, time

To do:
- long text scrolling
- custom json file (key: str) to add to text_json


2023-05-08 - v 1.0.0
2023-05-10 - v 1.1.0
- fixed bug with stock market crawling
- fixed bug if the image is not a real image
- added try-except blocks for stock & weather web calls
2023-06-13 - v 1.2.0
- changed to use recursive scan for folders instead of glob
- fixed bug if default folder (F1) does not exist - return error
2023-12-21 - v 1.3.0
- added dust effects

keys:
X = next text 
d = turn dust on/off if dust setup
SPACE = next image
ESC = exit

"""

import sys
import datetime
import os
import yaml
import glob
import random
import pygame
from pygame.locals import *
from common import *

from stock import Stock
from weather import Weather
from text_img import TxtImg


VERSION = "1.3.0"


class Dust():
    """class to represent floating dust on the screen"""
    dust_img = None
    x = y = 0
    max_x = max_y = 0

    xv = yv = fv = 0
    xvv = yvv = 1.0

    alive_flag = False

    def __init__(self, dust_img, max_x, max_y):
        # dust not faded out of existance yet
        self.alive_flag = True

        self.dust_img = dust_img
        # scale dust image, assume aspect ratio = 1.0
        xsize = ysize = random.randint(2,20)
        #ysize = random.randint(2,30)
        self.dust_img = pygame.transform.scale(self.dust_img, (xsize, ysize))        

        # random x & y velocity
        self.xv = random.randint(-7, 7)
        self.yv = random.randint(-7, 7)

        # minor changes to xv & yv so movement isn't so linear
        self.xvv = random.randint(-33, 33)/100
        self.yvv = random.randint(-33, 33)/100

        # staring alpha
        self.fade = random.randint(0, 25)
        # fade in string
        self.fv = random.randint(1, 20)
        

        # x & y starting coordinates
        self.max_x = max_x
        self.max_y = max_y
        self.x = random.randint(0, max_x)
        self.y = random.randint(0, max_y)

        #img.get_width(), img.get_height()


    def float(self):
        """change alpha, move x & y""""
        if self.alive_flag:
            self.fade += self.fv
            
            if self.fade < 5:
                self.alive_flag = False
            elif self.fade >= 160: # 255
                self.fv = -self.fv
            
            if self.alive_flag:
                self.dust_img.set_alpha(self.fade)

        if self.alive_flag:
            self.x += int(self.xv)
            self.y += int(self.yv)

            if self.x > self.max_x:
                self.alive_flag = False
            if self.x < 0:
                self.alive_flag = False
            if self.y > self.max_y:
                self.alive_flag = False
            if self.y < 0:
                self.alive_flag = False

            self.xv = self.xv + self.xvv
            self.xv = self.xv + self.yvv
        

def get_img_list(collection):
    """get the files in the path"""
    img_path = config.get(collection, {}).get("path")

    # use default (F1) if the path doesn't exist
    if not img_path:
        img_path = config.get("F1", {}).get("path")

    print("scanning: {}".format(img_path))

    #img_list = glob.glob(os.path.join(img_path))
    
    # error recursive scan
    img_list = []
    for root, dirs, files in os.walk(os.path.dirname(img_path)):
        for img in files:
            img_list.append(os.path.join(root, img))
    

    if not img_list and collection == "F1":
        print(f"error - no images found in default folder: {img_path}")
        sys.exit(1)

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
    bg_flag = config.get("screen", {}).get("use_image_color", False)
    text_config = config.get("text", {})
    bg_font = pygame.font.Font(text_config.get("bg_font"),
                               text_config.get("bg_font_size"))

    text_color = convert_color(text_config.get("color", "#FFFFFF"))
    text_shadow_color = convert_color(text_config.get("bg_color", "#000000"))
    text_shadow_offset = text_config.get("bg_offset", 48)
    text_padding = text_config.get("padding", 25)
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
    img_x = 0

    new_img_flag = True
    redraw_flag = True
    stretch_flag = False
    done = False

    # dust
    ixx = config.get("dust_image")
    dust_flag = False
    dust_list = []
    max_dust = config.get("max_dust", 0)
    if ixx:
        ixx_img = pygame.image.load(ixx).convert_alpha()

        clr = pygame.Color(255,255,255)
        for x in range(ixx_img.get_width()):
            for y in range(ixx_img.get_height()):
                clr.a = ixx_img.get_at((x, y)).a  # Preserve the alpha value.
                ixx_img.set_at((x, y), clr)  # Set the color of the pixel.


        
        
        dcnt = 0
        for d in range(1, max_dust):
            dust = Dust(ixx_img, screen_x, screen_y)
            dcnt += 1
            dust.id = f"dust-{dcnt}"
            dust_list.append(dust)
        dust_flag = True
    
    
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
            
                #print("Stock market updating ...")
                for s in stock_list:
                    s.update()
                    text_json[s.symbol] = str(s)
                stock_sec = now.timestamp() + stock_max_sec 

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
                if not my_img:
                    print("- error with image: {}".format(the_img))
                    my_img = old_img

                if bg_flag:
                    # get a random pixel from first 25 pixels in top left corner
                    background_color = my_img.get_at((random.randint(1,25), random.randint(1,25)))

                # reset new image timer
                new_img_flag = False
                redraw_flag = True
                if fade_speed > 0:
                    fade_in = 0
            else:
                print("- {} is not an image".format(the_img))
        
        if redraw_flag:

            bg.fill(background_color)

            

            if old_img and fade_speed > 0:
                old_img.set_alpha(255 - fade_in)
                bg.blit(old_img, (old_img_x, old_img_y))

            if my_img:
                if fade_in <= 255:
                    my_img.set_alpha(fade_in)
            
                bg.blit(my_img, (img_x, img_y))

            if img_x > 10:
                if stretch_flag:
                    iw, ih = my_img.get_rect().size
                    for y0 in range(0, screen_y):
                        
                        #c = my_img.get_at((1, y0))
                        c = bg.get_at((int(img_x), y0))
                        #print(img_x, y0, c)
                        #c = (int(y0/screen_y * 255),int(y0/screen_y * 255),int(y0/screen_y * 255), 255)
                        pygame.draw.lines(bg, c, False, [(0, y0), (img_x, y0)], 1)

                        c = bg.get_at((int(img_x)+iw-1, y0))
                        pygame.draw.lines(bg, c, False, [(img_x+iw, y0), (screen_x, y0)], 1)
            


            # time textbox
            time_obj.render_text_shadow()
            time_obj.render_text()

            # stock, weather, etc
            text_obj.render_text_shadow()
            text_obj.render_text()
  
            if dust_flag:
                #print("dddd - {}".format(len(dust_list)))
                for d in dust_list:
                    d.float()
                    #print(d.id, d.x, d.y) #, screen_x, screen_y)
                    if d.alive_flag:
                        bg.blit(d.dust_img, (d.x, d.y))
                    else:
                        dust_list.remove(d)

                if len(dust_list) < max_dust:
                    for d in range(1, max_dust - len(dust_list)):
                        if random.random() > 0.85:
                        
                            dcnt += 1
                            dust = Dust(ixx_img, screen_x, screen_y)
                            dust.id = f"dust-{dcnt}"
                            dust_list.append(dust)



            screen.blit(bg, (0, 0))
            pygame.display.flip()
            
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

                if event.key == K_s:
                    stretch_flag = not stretch_flag

                if event.key == K_d:
                    dust_flag = not dust_flag



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

    print(f"Background rotator - {VERSION}")

    config_file = "config.yaml"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    print(f"Loading config: {config_file}")
    

    if not os.path.isfile(config_file):
        print(f"Cannot find config: {config_file}")
        sys.exit(2)
    
    with open(config_file, "r", encoding="utf-8") as fh:
        try:
            config = yaml.load(fh, Loader=yaml.FullLoader)
        except yaml.scanner.ScannerError as err: 
            print("Config file error: {}".format(err))
            sys.exit(2)

    # full screen option
    screen, screen_x, screen_y = init_screen(config.get("screen", {}).get("full_screen", False))

    background(screen, screen_x, screen_y)

    pygame.quit()
    
    sys.exit(0)

