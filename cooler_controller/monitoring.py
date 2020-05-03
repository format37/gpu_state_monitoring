import RPi.GPIO as GPIO                                            
import time
import datetime
import os
import requests

def set_servo(p,val):
	p.start(2.5) # Initialization
	p.ChangeDutyCycle(val)
	print(datetime.datetime.now(), 'rig coolers speed set to', val)
	time.sleep(2)
	p.stop()

print(datetime.datetime.now(), 'started')
	
#rig coolers init
temp_treshold_bottom	= 73
temp_treshold_top		= 75
servo_state_bottom		= 5
servo_state_top			= 12
servo_val				= servo_state_bottom
url     				= "http://192.168.1.11:8080/gpustate"
servoPIN = 20
GPIO.setmode(GPIO.BCM)                                     
GPIO.setup(servoPIN, GPIO.OUT)                             
p = GPIO.PWM(servoPIN, 50) # GPIO for PWM with 50Hz
set_servo(p,servo_val)
	
while(True):
	temp	= float(requests.get(url).text)
	print(datetime.datetime.now(), 'rig temp:', temp)
	if temp>temp_treshold_top and servo_val<servo_state_top:
		servo_val+=1
		set_servo(p,servo_val)
	if temp<temp_treshold_bottom and servo_val>servo_state_bottom:
		servo_val-=1
		set_servo(p,servo_val)
	time.sleep(20)

GPIO.cleanup()
os._exit(1)