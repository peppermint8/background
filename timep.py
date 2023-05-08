#!/usr/bin/env python
'''
sudo apt-get install python-pygame

msg_list
0 = day of week
1 = date
2 = weather
3 = DOW
4 = S&P
5 = Nasdaq
6 = MSFT
7 = cpu temp
8 = cpu load


'''
import os
import pygame
from pygame.locals import *
import datetime
import sys
import random
import glob
import math

CZ = 3 * math.pi / 4
msg_list = []
config = {}

# rotate(r, 100, cx, cy)
def rotate(r, size, cx, cy):
    r0 = r - CZ
    x = math.cos(r0) * size - math.sin(r0) * size + cx
    y = math.sin(r0) * size + math.cos(r0) * size + cy

    x = int(x)
    y = int(y)
    return x,y

def get_stock(msg_list):
    f = config['stock'] #"/share/stock.txt"
    stock_str = ""
    change_mod = ""
    if os.path.isfile(f):
        stock_list = []
        fh = open(f, "r")
        for line in fh:
            #stock_list.append(line.strip())
            #print(line)
            arr = line.strip().split("|")
            mod = "+"
            if len(arr) == 3:
                if float(arr[2]) < 0:
                    mod = ""
                stock_str = "%s: %s %s%s" % (arr[0], arr[1], mod, arr[2])
                if arr[0] == "Dow":
                    msg_list[3] = stock_str
                elif arr[0] == "S&P 500":
                    msg_list[4] = stock_str
                elif arr[0] == "Nasdaq":
                    msg_list[5] = stock_str
                else:
                    msg_list[6] = stock_str
            
        fh.close()

    

def get_file_value(config_key):
    
    my_buffer = ""
    f_name = config.get(config_key, "/tmp/x")
    if os.path.isfile(f_name):
        fh = open(f_name, "r")
        for line in fh:
            my_buffer += line.strip()
        fh.close()
        
    return my_buffer

def get_weather():
    f = config['weather'] #"/share/weather.txt"

    weather_str = ""
    
    if os.path.isfile(f):
        fh = open(f, "r")
        for line in fh:
            weather_str += line.strip()
        fh.close()


    #msg_list[2] = weather_str[:32]
    return weather_str[:32]
    

def get_cpu_temp():
    f = config['cpu_temp']
    cpu_temp_str = ""
    if os.path.isfile(f):
        fh = open(f, "r")
        for line in fh:
            cpu_temp_str += line.strip()
        fh.close()
        
    
    #msg_list[3] = cpu_temp_str
    return cpu_temp_str
    
def get_cpu_load():
    f = config['cpu_load']
    load_str = ""
    if os.path.isfile(f):
        fh = open(f, "r")
        for line in fh:
            load_str += line.strip()
        fh.close()
        
    
    #msg_list[4] = load_str
    return load_str

def get_wh(iw, ih, max_x, max_y):

    new_w = iw * float(config['width_adjustment'])
    new_h = ih
    
    w1 = new_w / float(max_x)
    h1 = new_h / float(max_y)
    
    #print w1, h1
    if iw == 1920 and ih == 1200:
        new_w = max_x
        new_h = max_y
    elif iw == 2560 and ih == 1440:
        new_w = max_x
        new_h = max_y
    elif iw == 2048 and ih == 1163:
        new_w = max_x
        new_h = max_y
    elif w1 > h1:
        new_w = new_w / w1
        new_h = new_h / w1
    else:
        new_w = new_w / h1
        new_h = new_h / h1
        
    new_w = int(new_w)
    new_h = int(new_h)
    
    #print "w = %s/%s   h = %s/%s" % (iw, new_w, ih, new_h)
    
    return new_w, new_h

def get_wh2(iw, ih, max_x, max_y):
    #print iw, ih, max_x, max_y
    
    new_w = iw
    
    new_h = ih
    #print iw, ih
    if iw == 1920 and ih == 1200:
        new_w = max_x
        new_h = max_y
    elif iw > ih:
        new_w = max_x
        new_h = int(ih * (max_x / float(iw)))
    else:
        new_h = max_y
        new_w = int(iw * (max_y / float(ih)))
        new_w = int(new_w * float(config['width_adjustment']))
        #new_w = int(new_w * 0.76) # monitor correction
    #print iw, ih, max_x, max_y, new_w, new_h
    
    return new_w, new_h


def load_img(mode):
    img_list = []

    if mode == "a":
        if config['folder_1']:
            img_list = glob.glob("%s/*.jpg" % config['folder_1'])
    if mode == "b":
        if config['folder_2']:
            img_list = glob.glob("%s/*.jpg" % config['folder_2'])
    if mode == "c":
        if config['folder_3']:
            img_list = glob.glob("%s/*.jpg" % config['folder_3'])
    if mode == "d":
        if config['folder_4']:
            img_list = glob.glob("%s/*.jpg" % config['folder_4'])
    if mode == "e":
        if config['folder_5']:
            img_list = glob.glob("%s/*.jpg" % config['folder_5'])
    if mode == "f":
        if config['folder_6']:
            img_list = glob.glob("%s/*.jpg" % config['folder_6'])

    # use folder 1 if nothing set
    if len(img_list) == 0:
        img_list = glob.glob("%s/*.jpg" % config['folder_1'])
    #print "mode = %s, %s" % (mode, len(img_list))
    return img_list

def main():
    # Initialize screen
    pygame.init()

    infoObject = pygame.display.Info()
    print("screen %s x %s" % (infoObject.current_w, infoObject.current_h))
    max_x = infoObject.current_w
    max_y = infoObject.current_h
    #screen = pygame.display.set_mode((max_w, max_h), FULLSCREEN)       
    
    
    screen = pygame.display.set_mode((max_x, max_y), FULLSCREEN)
    pygame.display.set_caption('Time Clock')
    clock = pygame.time.Clock()
    now = datetime.datetime.now()
    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))

    pygame.mouse.set_visible(False)
    norm_font = pygame.font.Font(config['font'], int(config['font_size']))

    days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    msg_list = ['dow','date','weather','dow','nasdaq','s&p','msft', 'cpu_temp', 'cpu_load']
    date_str = "%s-%02d-%02d" % (now.year, now.month, now.day)
    msg_list[1] = date_str
    dow_str = days[now.weekday()]
    msg_list[0]  = dow_str
    img_list_id = "a"
    blank_screen = False
    
    get_stock(msg_list)
    msg_list[2] = get_file_value("weather")
    msg_list[7] = get_file_value("cpu_temp")
    msg_list[8] = get_file_value("cpu_load")
    
    #print msg_list
    #sys.exit(44)
    
    img_list = load_img("a")

    r = random.randint(1,len(img_list))
    the_img = img_list[r-1]

    
    
        
    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()

    bg_color = (0,0,0)
    rgb1 = (255,255,255)
    rgb0 = (0,0,0)
    last_sec = -1
    sec_cnt = 0
    sec_target = int(config['delay'])
    
    img_x = 0
    img_y = 0
    
    # Event loop
    done = False
    iw = 0
    ih = 0
    if os.path.isfile(the_img):
        my_img = pygame.image.load(the_img).convert()
        iw, ih = my_img.get_rect().size # 512 x 768
    new_w, new_h = get_wh(iw, ih, max_x, max_y)
    img_x = int((max_x - new_w)/2.0)
    img_y = int((max_y - new_h)/2.0)
    my_img = pygame.transform.scale(my_img, (new_w, new_h))
    
    my_text = msg_list[0][:40]
    
    while not done:
        
        
        now = datetime.datetime.now()

        
        if now.second != last_sec:
            sec_cnt += 1
            background.fill(bg_color)
            
            
            if not blank_screen:
                background.blit(my_img, (img_x, img_y))
                
                #date_str = "%s-%02d-%02d" % (now.year, now.month, now.day)
                #msg_list[1] = date_str
                #dow_str = days[now.weekday()]
                #msg_list[0]  = dow_str
                #print now.second, msg_list
                
                ampm = "am"
                hr = now.hour
                if now.hour >= 12:
                    ampm = "pm"
                if hr > 12:
                    hr = now.hour - 12
                if hr == 0:
                    hr = 12
    
    
                        
                #my_str = "%d:%02d:%02d %s" % (hr, now.minute, now.second, ampm)
                my_str = "%d:%02d %s" % (hr, now.minute, ampm)
                
                date_str = "%s-%02d-%02d" % (now.year, now.month, now.day)
                msg_list[1] = date_str
                dow_str = days[now.weekday()]
                msg_list[0]  = dow_str
    
                
                time_text = norm_font.render(my_str, 1, rgb0)
                text_xy = time_text.get_rect()
                my_x = max_x - text_xy[2] - 48
                my_y = max_y - text_xy[3] - 48
        
                background.blit(time_text, (my_x, my_y))
                #print my_x, my_y, my_str
                
                time_text = norm_font.render(my_str, 1, rgb1)
                my_x = max_x - text_xy[2] - 50
                my_y = max_y - text_xy[3] - 50
                background.blit(time_text, (my_x, my_y))
    
                try:
                    msg_text = norm_font.render(my_text, 1, rgb0)
                    #msg_xy = msg_text.get_rect()
                    background.blit(msg_text, (52, 52))
                    msg_text = norm_font.render(my_text, 1, rgb1)
                    #msg_xy = msg_text.get_rect()
                    background.blit(msg_text, (50, 50))
                except pygame.error:
                    pass
                    # width or height too big

            #ypos1 = ypos1+1
            
        last_sec = now.second
        
        if last_sec % 15 == 0:
            r = random.randint(1,len(msg_list))
            my_text = msg_list[r-1]            
        
        if sec_cnt >= sec_target:
            sec_cnt = 0
            #sec_target = random.randint(15, 180) 
            #sec_target = 20
            

            
            get_stock(msg_list)
            msg_list[2] = get_file_value("weather")
            msg_list[7] = get_file_value("cpu_temp")
            msg_list[8] = get_file_value("cpu_load")
    
            if not blank_screen:

                if len(img_list) == 0:
                    img_list = load_img(img_list_id)
                    
                r = random.randint(1,len(img_list))
                the_img = img_list[r-1]
                img_list.remove(the_img)
                
                #print(the_img)
                try:
                    my_img = pygame.image.load(the_img).convert()
                except pygame.error as e:
                    print("image error: {}".format(e))
                    print("image: {}".format(the_img))
                
            
                iw, ih = my_img.get_rect().size # 512 x 768
                new_w, new_h = get_wh(iw, ih, max_x, max_y)
    
                #my_img = pygame.transform.scale(my_img, (max_x, max_y))
                my_img = pygame.transform.scale(my_img, (new_w, new_h))
                img_x = int((max_x - new_w)/2.0)
                img_y = int((max_y - new_h)/2.0)            

            
        
        #background.blit(my_img, (-500,20))
        
        

    
        for event in pygame.event.get():
            if event.type == QUIT:
                done = True
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    done = True
                #elif event.key == K_F1:
                #    img_list = load_img("a")
                #elif event.key == K_F2:
                #    img_list = load_img("b")

        all_keys = pygame.key.get_pressed()
        if all_keys[pygame.K_F1] and all_keys[pygame.K_LSHIFT]:
            img_list_id = "a"
            img_list = load_img("a")
            blank_screen = False
            sec_cnt = sec_target
        if all_keys[pygame.K_F2] and all_keys[pygame.K_LSHIFT]:
            img_list_id = "b"
            img_list = load_img("b")
            blank_screen = False
            sec_cnt = sec_target
        if all_keys[pygame.K_F3] and all_keys[pygame.K_LSHIFT]:
            img_list_id = "c"
            img_list = load_img("c")
            blank_screen = False
            sec_cnt = sec_target            
        if all_keys[pygame.K_F4] and all_keys[pygame.K_LSHIFT]:
            img_list_id = "d"
            img_list = load_img("d")
            blank_screen = False
            sec_cnt = sec_target            
        if all_keys[pygame.K_F5] and all_keys[pygame.K_LSHIFT]:
            img_list_id = "e"
            img_list = load_img("e")
            blank_screen = False
            sec_cnt = sec_target    
        if all_keys[pygame.K_F6] and all_keys[pygame.K_LSHIFT]:
            img_list_id = "f"
            img_list = load_img("f")
            blank_screen = False
            sec_cnt = sec_target    

        if all_keys[pygame.K_x]:
            blank_screen = True
            img_list_id = "a"
            img_list = load_img("a")
            
        if all_keys[pygame.K_SPACE]:
            sec_cnt = sec_target
            
        #for _ in range(100):
        #    x = random.randint(0,cx*2)
        #    y = random.randint(0,cy*2)
        #    pygame.draw.circle(background, (0,255,0), (x, y), 2, 0)

        screen.blit(background, (0, 0))
        pygame.display.flip()
        
        
        clock.tick(15) # at most 5 frames should pass per second
        #print now.microsecond
    pygame.mouse.set_visible(True)    
    pygame.quit()
    return


if __name__ == '__main__':
    #msg_list = []

    # defaults
    config = {
        "delay" : 30,
        "folder_1" : "/disk2/doom/cc/chromecast1200/",
        "font" : "/share/fonts/CheyenneSans-Regular.ttf",
        "font_size" : 64,
        "width_adjustment" : 1,
        "stock" : "/share/stock.txt",
        "weather" : "/share/weather.txt",
        "cpu_temp": "/share/cpu_temp.txt",
        "cpu_load": "/share/loadavg.txt"
    }
    
    time_cfg = os.path.join(os.getenv("HOME"), ".timep.cfg")
    if os.path.isfile(time_cfg):
        fh = open(time_cfg, "r")
        for line in fh:
            if line.strip().startswith("#"):
                continue
            arr = line.split("=")
            if "=" in line:
                config[str(arr[0]).strip()] = str(arr[1]).strip()
        fh.close()
    

    main()


    
    print("Later")
    sys.exit(0)
    
