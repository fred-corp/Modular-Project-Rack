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
  return round(temp, 1)

def get_RAM():
  ram = psutil.virtual_memory().percent
  return ram

# Draw Legends
draw.text((2, 18), 'CPU  :', font=font, fill=255)
draw.text((2, 34), 'Temp :', font=font, fill=255)
draw.text((2, 50), 'RAM  :', font=font, fill=255)

while True:
  # IP
  private_ip = get_IP()
  # Draw IP
  draw.rectangle(xy=[(0, 0), (127, 15)], fill=255, outline=0)
  draw.text(((6*len(private_ip))/2, 2), str(private_ip), font=font, fill=0)

  # Draw blanking rectangle
  draw.rectangle(xy=[(40, 16), (127, 63)], fill=0, outline=0)


  # CPU
  cpu_pct = get_CPU()
  # Draw CPU Text
  draw.text((40, 18), str(cpu_pct) + '%', font=font, fill=255)

  # Draw CPU Graph
  draw.line(xy=[(72, 30), (127, 30)], fill=255, width=1)
  draw.line(xy=[(72, 18), (72, 30)], fill=255, width=1)


  # Temp
  temp = get_Temp()
  # Draw Temp
  draw.text((40, 34), str(temp) + 'C', font=font, fill=255)

  # Draw Temp Graph
  draw.line(xy=[(72, 46), (127, 46)], fill=255, width=1)
  draw.line(xy=[(72, 34), (72, 46)], fill=255, width=1)


  # RAM
  ram = get_RAM()
  # Draw RAM
  draw.text((40, 50), str(ram) + '%', font=font, fill=255)

  # Draw RAM Graph
  draw.line(xy=[(72, 62), (127, 62)], fill=255, width=1)
  draw.line(xy=[(72, 50), (72, 62)], fill=255, width=1)

  oled.image(image)
  oled.display()

  time.sleep(2.5)
