import RPi.GPIO as GPIO                                            
import time                                                        
import os
import requests

temp_treshold_bottom	= 74
temp_treshold_top		= 75
servo_state_bottom		= 5
servo_state_top			= 12
servo_val				= servo_state_bottom

def set_servo(p,val):
	p.start(2.5) # Initialization
	p.ChangeDutyCycle(val)
	print('rig coolers speed set to '+str(val))
	time.sleep(2)
	p.stop()

try:
	servoPIN = 20
	GPIO.setmode(GPIO.BCM)                                     
	GPIO.setup(servoPIN, GPIO.OUT)                             
	p = GPIO.PWM(servoPIN, 50) # GPIO for PWM with 50Hz
	
	while(True):
		url     = "http://192.168.1.11:8080/gpustate"
		temp	= int(requests.get(url,headers = headers))
		if temp>temp_treshold_top and servo_val<servo_state_top:
			servo_val+=1
			set_servo(p,servo_val)
		if temp<temp_treshold_bottom and servo_val>servo_state_bottom:
			servo_val-=1
			set_servo(p,servo_val)
		
		time.sleep(10)
	
except:
	pass
finally:
	GPIO.cleanup()
	os._exit(1)
