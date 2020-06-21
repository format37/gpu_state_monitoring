import RPi.GPIO as GPIO
import time
import datetime
import os
import requests
import urllib
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)
farm_chat = "-227727734"

def send_to_telegram(chat,message):
	headers = {
    "Origin": "http://scriptlab.net",
    "Referer": "http://scriptlab.net/telegram/bots/relaybot/",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'}

	url	= "http://scriptlab.net/telegram/bots/relaybot/relaylocked.php?chat="+chat+"&text="+urllib.parse.quote_plus(message)
	requests.get(url,headers = headers)

class Rig():

	def __init__(
			self, 
			name, 
			channel, 
			url,
			treshold_bottom = 76, 
			treshold_top = 78, 
			servo_bottom = 10,
			servo_top = 100,
			servo_state = 30
			):
		self.name				= name
		self.channel				= channel
		self.url				= url
		self.treshold_bottom		= treshold_bottom
		self.treshold_top		= treshold_top
		self.servo_bottom		= servo_bottom
		self.servo_top			= servo_top
		self.servo_state		= servo_state
		#GPIO.setup(self.pin, GPIO.OUT)
		kit.servo[channel].actuation_range = 100
		#self.servo = GPIO.PWM(self.pin, 50) # GPIO for PWM with 50Hz
		self.enabled			= True
		try:
			self.temp = self.get_temp()
			#self.servo.start(2.5) # Initialization
			#self.enabled	= True
			self.set_servo()
		except Exception as e:
			message = str(datetime.datetime.now())+' '+self.name+' disabled. ERR: unable to get temperature by link:\n'+self.url+'\n'+str(e)
			print(message)
			send_to_telegram(farm_chat,message)
			self.temp		= 0
			#self.enabled	= False

	def get_temp(self):
		self.temp	= float(requests.get(self.url).text)

	def set_servo(self):

		#self.servo.ChangeDutyCycle(self.servo_state)
		#print(datetime.datetime.now(), self.name, 'with temp', self.temp, ' coolers speed set to', self.servo_state)
		kit.servo[self.channel].angle = self.servo_state
		#time.sleep(2)
		#self.servo.stop()

	def update(self):
		if self.enabled:
			try:
				self.get_temp()
			except Exception as e:
				message = str(datetime.datetime.now())+' '+self.name+' disabled. ERR: unable to get temperature by link:\n'+self.url+'\n'+str(e)
				print(message)
				send_to_telegram(farm_chat,message)
				#self.enabled = False
			print(self.name,self.temp)
			if self.enabled:
				if self.temp>self.treshold_top and self.servo_state<self.servo_top:
					self.servo_state +=1
					self.set_servo()
				if self.temp<self.treshold_bottom and self.servo_state>self.servo_bottom:
					self.servo_state -=1
					self.set_servo()

try:
	GPIO.cleanup()
except:
	pass

print(datetime.datetime.now(), 'started')

GPIO.setmode(GPIO.BCM)

#enable primary cooler
GPIO.setup(27, GPIO.OUT)
GPIO.output(27, GPIO.LOW)

rigs=[]
rigs.append( Rig("Rig1",0,"http://192.168.1.11:8080/gpustate") )
rigs.append( Rig("Rig2",1,"http://192.168.1.23:8080/gpustate") )

send_to_telegram(farm_chat,str(datetime.datetime.now())+" farm cooler controller started")

while(True):
	rigs[0].update()
	rigs[1].update()
	time.sleep(1)
