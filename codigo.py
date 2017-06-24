#!/usr/bin/python3

#importamos las librerias
import httplib, urllib
import time
from time import localtime, strftime
import psutil
import spidev
import os
import smtplib


# abrir SPI bus
spi = spidev.SpiDev()
spi.open(0,0)

email = 0
L1=600 #limite para realizar regado, Seco de 600 a 1023
L2=400 #limite de humedad  humedo de 400 a 600
	# Tierra mojada de 0 a 399

# Funcion para leer el ADC MCP3008 por spi
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data

#Funcion para el envio de emails
def send_email(num):           
            gmail_user = "w3ndy.carib3l@outlook.com"
            gmail_pwd = "Wcaribel.2"
            FROM = 'w3ndy.carib3l@outlook.com'
            TO = ['w3ndy.carib3l@gmail.com'] 
            SUBJECT ="Tu planta necesita Agua"
            TEXT = "Hola, soy tu planta y necesito agua! Este es el correo No. " + str(num) + " de 5"

            # Prepare actual message
            message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
            try: 
                server = smtplib.SMTP("smtp.live.com", 587) 
                server.ehlo()
                server.starttls()
                server.login(gmail_user, gmail_pwd)
                server.sendmail(FROM, TO, message)
                server.close()
                print ('successfully sent the mail')
            except:
                print ("failed to send mail")


def doit():
	global email
	
	cpu_pc = psutil.cpu_percent()
	adc_data = ReadChannel(0)
        print(adc_data)
	print(strftime("%a, %d %b %Y %H:%M:%S", localtime()))


	params = urllib.urlencode({'field1': cpu_pc, 'field2': adc_data,'key':'UD9MLPIQ85K1HFA6'})
	headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
	conn = httplib.HTTPConnection("api.thingspeak.com:80")

	if adc_data > L1:
		print ("Ayura!! Necesito Agua, te enviare un email para que no lo olvides ( varios en realidad)")
		print("Ya enserio necesito agua, se han enviado " + str(email) + " emails")
		if email < 5:
                                email+=1
                                send_email(email)
	else:
		if adc_data >L2:
			print("La humedad actual es suficiente, pero no por mucho tiempo")
	
		else:
			print("Mi tierra esta mojada, puedes estar despreocupado")
			email=0
	try:
		conn.request("POST", "/update", params, headers)
		response = conn.getresponse()
		#print(response.status, response.reason)
		data = response.read()
		conn.close()
	except:
			print("connection failed")	

#sleep for 16 seconds (api limit of 15 secs)
if __name__ == "__main__":
	time.sleep(1)
        print ("Iniciando Sistema de Monitoreo de Humedad del Suelo")
	time.sleep(2)

	while True:
		doit()
time.sleep(18) 
