import time
import board
import neopixel
from math import inf
import ephem
import datetime

#Observation point 
latitude, longitude = '51.4545', '2.5879'

#Choose planet colours - defaults are jazzier than real life. 
#ref https://www.schemecolor.com/venus-planet-colors.php
mercury = { "name":"mercury", "RGB":[(231,232,236),(104,105,109)], "orbit":ephem.Mercury(), "twinkliness":500000, "next_rise_time":0, "previous_rise_time":0, "next_set_time":0, "previous_set_time":0, "constellation": None, "visibility": None}
venus = { "name":"venus", "RGB":[(139, 145, 161),(187, 183, 171),(221, 216, 212),(239, 239, 239)], "orbit":ephem.Venus(), "twinkliness":7000000,"next_rise_time":0, "previous_rise_time":0, "next_set_time":0, "previous_set_time":0, "constellation": None, "visibility": None}
earth = { "name":"the sun", "RGB":[(0,169,95),(0,50,220)], "orbit":ephem.Sun(), "twinkliness":1000000,"next_rise_time":0, "previous_rise_time":0, "next_set_time":0, "previous_set_time":0, "constellation": None, "visibility": None} #value for sun used to indicate if it is light or dark
mars = { "name":"mars", "RGB":[(123,38,14),(173,56,0)], "orbit":ephem.Mars(), "twinkliness":1200000,"next_rise_time":0, "previous_rise_time":0, "next_set_time":0, "previous_set_time":0, "constellation": None, "visibility": None}
jupiter = { "name":"jupiter", "RGB":[(201,144,57),(227,220,203)], "orbit":ephem.Jupiter(), "twinkliness":1400000,"next_rise_time":0, "previous_rise_time":0, "next_set_time":0, "previous_set_time":0, "constellation": None, "visibility": None}
saturn = { "name":"saturn", "RGB":[(234,214,184),(206,206,106)], "orbit":ephem.Saturn(), "twinkliness":1600000,"next_rise_time":0, "previous_rise_time":0, "next_set_time":0, "previous_set_time":0, "constellation": None, "visibility": None}
uranus = { "name":"uranus", "RGB":[(75,238,88),(67,201,130)], "orbit":ephem.Uranus(), "twinkliness":2000000,"next_rise_time":0, "previous_rise_time":0, "next_set_time":0, "previous_set_time":0, "constellation": None, "visibility": None}
neptune = { "name":"neptune", "RGB":[(91,93,223),(113,173,219)], "orbit":ephem.Neptune(), "twinkliness":2200000,"next_rise_time":0, "previous_rise_time":0, "next_set_time":0, "previous_set_time":0, "constellation": None, "visibility": None}
planets = [mercury, venus, earth, mars,jupiter,saturn,uranus,neptune]


# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18

# The number of NeoPixels inside the star/sun
sun_pixels = 25
planet_pixels = len(planets)
num_pixels = planet_pixels + sun_pixels


# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.RGB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.4, auto_write=False, pixel_order=ORDER)


def wheel_disco(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)

def wheel_dev(pos):
    if (pos%25)%5 == 1:     
        r = 200
        g = 200
        b = 0
    else:
        r = g = b = 0

    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)

def sun_cycle(enthusiasm):
    #rotate faster when there are more planets overhead 
    if is_dark():  
        rotation = int(time.time()*(100+enthusiasm))%255     
        for i in range(sun_pixels):        
            pixel_index = (i * 256 // sun_pixels) + rotation
            pixels[i] = wheel_disco(pixel_index & 255)
    else:
        rotation = int(time.time()*(5))%sun_pixels
        for i in range(sun_pixels):        
            pixel_index = ((i +rotation) % sun_pixels)
            pixels[i] = wheel_dev(pixel_index)


def planet_cycle():
        #calculate planet RGB values and flash if they're visible
    for index, planet in enumerate(planets): 
        colours = len(planet["RGB"])
        phase_total = colours*2*abs((int(round(time.time()*1000000))%planet["twinkliness"])/planet["twinkliness"]-0.5)
        phase = phase_total%1
        phase_out = int(phase_total)%colours
        phase_in = int(phase_total+1)%colours
              
        
        # if the planet isn't over head then don't modulate the brightness
        if not planet["visibility"]:
            blink = 1.0
        # if it is dark & the planet is overhead then modulate between zero and full brightness
        elif is_dark():
            blink = 2*abs((int(round(time.time()*500000))%planet["twinkliness"])/planet["twinkliness"]-0.5)
        #if it is light and the planet is overhead then modulate between half and full brightness
        else:
            blink = abs((int(round(time.time()*500000))%planet["twinkliness"])/planet["twinkliness"]-0.5)+0.5
        
        
        r = int(blink*((1-phase)*planet["RGB"][phase_out][0] + phase*planet["RGB"][phase_in][0])) 
        g = int(blink*((1-phase)*planet["RGB"][phase_out][1] + phase*planet["RGB"][phase_in][1])) 
        b = int(blink*((1-phase)*planet["RGB"][phase_out][2] + phase*planet["RGB"][phase_in][2])) 

        pixels[sun_pixels+index] = (r,g,b)

def is_dark():    
    return not (earth["visibility"])

def update_planets():    
    #create a point of reference with the current system time
    my_house = ephem.Observer()
    my_house.lat, my_house.lon =  '51.4545', '2.5879'

    #set horizon at an elevation so planets arent reported as visible until they are high enough to see. 0.1 radians is approx 5 degrees
    
    calculation_schedule = inf
    count = 0
    
    #set horizon for sunset or visibility
    for planet in planets:    
        if planet["name"] == "earth":
            my_house.horizon = '-0.2'
        else:
            my_house.horizon = '0.1'  
            
        planet["orbit"].compute(my_house)  
        planet["previous_set_time"]= ephem.localtime(my_house.previous_setting(planet["orbit"]))      
        planet["next_set_time"]= ephem.localtime(my_house.next_setting(planet["orbit"]))
        planet["previous_rise_time"] = ephem.localtime(my_house.previous_rising(planet["orbit"]))
        planet["next_rise_time"] = ephem.localtime(my_house.next_rising(planet["orbit"]))
        planet["constellation"]= ephem.constellation(planet["orbit"])
        #print(planet["constellation"])


        
        if planet["previous_set_time"]<planet["previous_rise_time"]: #did the planet rise more recently than it set?
            planet["visibility"]=True
            print(planet["name"], " is overhead now")
            count+=1
        else:
            planet["visibility"]=False
            print(planet["name"], " next rises at ", planet["next_rise_time"])
        
        #note absence of localtime for proper comparison later
        calculation_schedule = min(calculation_schedule, my_house.next_rising(planet["orbit"]),my_house.next_setting(planet["orbit"]))
        
    print ("next transition ",calculation_schedule)
    return calculation_schedule, count

next_calculation = 0
while True:   
    #calculate rise and set times for the planets if previously calculated time has passed
    if ephem.Date(datetime.datetime.now()) > next_calculation:
        next_calculation, visible_planets = update_planets()

    planet_cycle()  #phase between two colour extremes and blink if visible
    sun_cycle(visible_planets*25)  # rainbow cycle 
    pixels.show()
