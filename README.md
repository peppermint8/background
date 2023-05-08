# Background Screen saver

Pygame screen saver - rotate through a folder of images (.jpg, .png)
images fade in every 30 seconds

Run with `bg.py` 

Shows current date & time
 - looks up weather using the weather api (you need your own key)
 - looks up stocks using yahoo finance api

## Requirements

Uses python 3.10 and pygame.

## Config

Edit config.yaml to change:
 - image folder locations
 - stock market trackers (Yahoo finance)
 - weather for your zipcode

You need to register at https://api.openweathermap.org to get your API key


use a different config by supplying a different yaml config
`bg.py config-2.yaml`

