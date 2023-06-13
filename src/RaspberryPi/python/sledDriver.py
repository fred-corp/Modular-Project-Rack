import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import psutil

oled = Adafruit_SSD1306.SSD1306_128_64(rst=None)
oled.begin()
oled.clear()
oled.display()

width = oled.width
height = oled.height
image = Image.new('1', (width, height))

font = ImageFont.load_default()

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

def get_IP():
  interfaces = psutil.net_if_addrs()
  IP = interfaces['eth0'][0].address
  return IP

def get_CPU():
  cpu = psutil.cpu_percent()
  return cpu

def get_Temp():
  temp = psutil.sensors_temperatures()['cpu_thermal'][0].current
  return temp

def get_RAM():
  ram = psutil.virtual_memory().percent
  return ram

while True:
  private_ip = get_IP()

  draw.rectangle(xy=[(0, 0), (127, 15)], fill=255, outline=0)
  draw.text(((6*len(private_ip))/2, 2), str(private_ip), font=font, fill=0)


  draw.text((4, 18), 'CPU', font=font, fill=255)
  draw.text((4, 34), 'Temp', font=font, fill=255)
  draw.text((4, 50), 'RAM', font=font, fill=255)

  draw.rectangle(xy=[(60, 16), (127, 63)], fill=0, outline=0)

  draw.text((60, 18), str(get_CPU()) + '%', font=font, fill=255)
  draw.text((60, 34), str(get_Temp()) + 'C', font=font, fill=255)
  draw.text((60, 50), str(get_RAM()) + '%', font=font, fill=255)


  # Display image.
  oled.image(image)
  oled.display()