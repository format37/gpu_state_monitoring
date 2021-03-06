import RPi.GPIO as GPIO                                            
import time
import datetime
import os
import requests
import urllib

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
			pin, 
			url,
			treshold_bottom = 75, 
			treshold_top = 76, 
			servo_bottom = 5, 
			servo_top = 12, 
			servo_state = 10
			):
		self.name				= name
		self.pin				= pin
		self.url				= url
		self.treshold_bottom	= treshold_bottom
		self.treshold_top		= treshold_top
		self.servo_bottom		= servo_bottom
		self.servo_top			= servo_top
		self.servo_state		= servo_state		
		GPIO.setup(self.pin, GPIO.OUT)
		self.servo = GPIO.PWM(self.pin, 50) # GPIO for PWM with 50Hz
		try:
			self.temp = self.get_temp()
			self.servo.start(2.5) # Initialization
			self.enabled	= True
			self.set_servo()
		except:
			message = str(datetime.datetime.now())+' '+self.name+' disabled. ERR: unable to get temperature by link:\n'+self.url
			print(message)
			send_to_telegram(farm_chat,message)
			self.temp		= 0
			self.enabled	= False		

	def get_temp(self):
		self.temp	= float(requests.get(self.url).text)

	def set_servo(self):

		self.servo.ChangeDutyCycle(self.servo_state)
		print(datetime.datetime.now(), self.name, 'with temp', self.temp, ' coolers speed set to', self.servo_state)
		time.sleep(2)
		#self.servo.stop()

	def update(self):
		if self.enabled:
			try:
				self.get_temp()
			except:
				message = str(datetime.datetime.now())+' '+self.name+' disabled. ERR: unable to get temperature by link:\n'+self.url
				print(message)
				send_to_telegram(farm_chat,message)
				self.enabled = False

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
rigs.append( Rig("Rig1",20,"http://192.168.1.11:8080/gpustate") )
rigs.append( Rig("Rig2",21,"http://192.168.1.23:8080/gpustate") )

send_to_telegram(farm_chat,str(datetime.datetime.now())+" farm cooler controller started")

while(True):
	rigs[0].update()
	rigs[1].update()
	time.sleep(20)
