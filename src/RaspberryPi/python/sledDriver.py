import time
import psutil
import queue
import RPi.GPIO as GPIO
from socket import AddressFamily

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

max_temp_graph = 80
min_temp_graph = 15

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

button = 4
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Create display
oled = Adafruit_SSD1306.SSD1306_128_64(rst=None)
oled.begin()
oled.clear()
oled.display()

width = oled.width
height = oled.height
image = Image.new('1', (width, height))
font = ImageFont.load_default()
draw = ImageDraw.Draw(image)

# Create queues for graphs
cpu_graph_queue = queue.Queue(maxsize=width-72)
temp_graph_queue = queue.Queue(maxsize=width-72)
ram_graph_queue = queue.Queue(maxsize=width-72)

# Init queues for graphs
def init_graph_queues(zero=False):

  if zero:
    while not cpu_graph_queue.full():
      cpu_graph_queue.put(0)

    while not temp_graph_queue.full():
      temp_graph_queue.put(min_temp_graph)

    while not ram_graph_queue.full():
      ram_graph_queue.put(0)


def get_IP():
  interfaces = psutil.net_if_addrs()
  if psutil.net_if_addrs()['eth0'][0].family == AddressFamily.AF_INET:
    IP = interfaces['eth0'][0].address
  else:
    IP = "No IPV4"
  return IP

def get_CPU():
  cpu = psutil.cpu_percent()
  if cpu >= 100:
    cpu = 100
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

def update_queues():
  cpu_pct = get_CPU()
  if cpu_graph_queue.full():
    cpu_graph_queue.get()
  cpu_graph_queue.put(cpu_pct)

  temp = get_Temp()
  if temp_graph_queue.full():
    temp_graph_queue.get()
  temp_graph_queue.put(temp)

  ram = get_RAM()
  if ram_graph_queue.full():
    ram_graph_queue.get()
  ram_graph_queue.put(ram)


def drawDisplay():
  # IP
  private_ip = get_IP()
  # Draw IP
  draw.rectangle(xy=[(0, 0), (127, 15)], fill=255, outline=0)
  draw.text((64-((6*len(private_ip))/2), 2), private_ip, font=font, fill=0)

  # Draw blanking rectangle
  draw.rectangle(xy=[(40, 16), (127, 63)], fill=0, outline=0)


  # CPU
  # Draw CPU Text
  draw.text((40, 18), str(cpu_graph_queue.queue[cpu_graph_queue.qsize()-1]) + '%', font=font, fill=255)

  # Draw CPU Graph
  draw.line(xy=[(72, 30), (127, 30)], fill=255, width=1)
  draw.line(xy=[(72, 18), (72, 30)], fill=255, width=1)
  for i in range(0, cpu_graph_queue.qsize()):
    draw.point(xy=[(72+i, 30-((cpu_graph_queue.queue[i]/100)*12))], fill=255)


  # Temp
  # Draw Temp
  draw.text((40, 34), str(temp_graph_queue.queue[temp_graph_queue.qsize()-1]) + 'C', font=font, fill=255)

  # Draw Temp Graph
  draw.line(xy=[(72, 46), (127, 46)], fill=255, width=1)
  draw.line(xy=[(72, 34), (72, 46)], fill=255, width=1)
  for i in range(0, temp_graph_queue.qsize()):
    draw.point(xy=[(72+i, 46-((temp_graph_queue.queue[i]-min_temp_graph)/(max_temp_graph-min_temp_graph))*12)], fill=255)


  # RAM
  # Draw RAM
  draw.text((40, 50), str(ram_graph_queue.queue[ram_graph_queue.qsize()-1]) + '%', font=font, fill=255)

  # Draw RAM Graph
  draw.line(xy=[(72, 62), (127, 62)], fill=255, width=1)
  draw.line(xy=[(72, 50), (72, 62)], fill=255, width=1)
  for i in range(0, ram_graph_queue.qsize()):
    draw.point(xy=[(72+i, 62-((ram_graph_queue.queue[i]/100)*12))], fill=255)

  oled.image(image)
  oled.display()


if __name__ == '__main__':
  GPIO.add_event_detect(button, GPIO.FALLING)
  init_graph_queues(zero=True)
  display_refresh_interval = 2.5
  queue_refresh_interval = display_refresh_interval
  display_sleep_time = 30
  try:
    displaySleep = False
    displaySleepTimeLast = time.time()
    displayTimeLast = time.time()
    queueUpdateLast = time.time()
    while True:
      timeNow = time.time()

      if GPIO.event_detected(button):
        displaySleep = False
        displaySleepTimeLast = timeNow

      if not displaySleep and timeNow-displaySleepTimeLast >= display_sleep_time:
        oled.clear()
        oled.display()
        displaySleep = True
        displaySleepTimeLast = timeNow

      if timeNow-displayTimeLast >= display_refresh_interval and not displaySleep:
        drawDisplay()
        displayTimeLast = timeNow

      if timeNow-queueUpdateLast >= queue_refresh_interval:
        update_queues()
        queueUpdateLast = timeNow
      
      time.sleep(0.5)

  except KeyboardInterrupt:
    oled.clear()
    oled.display()
    print("\n")
    exit()
