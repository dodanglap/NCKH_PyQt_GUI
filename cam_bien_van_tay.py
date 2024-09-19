import sys
sys.path.append('/home/lapdo/NCKH/lib/python3.11/site-packages')

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
import time
import board
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint
from tkinter import messagebox
# Khởi tạo firebase
from firebase import firebase

import serial
import os


firebase = firebase.FirebaseApplication('https://fir-firebase-2eb50-default-rtdb.asia-southeast1.firebasedatabase.app', None)

def find_usb_serial_ports():
    # Lấy danh sách các file trong thư mục /dev
    devices = os.listdir('/dev')
    # Tìm các cổng serial như ttyUSB hoặc ttyACM
    usb_ports = [dev for dev in devices if 'ttyUSB' in dev or 'ttyACM' in dev]
    return usb_ports[0]

class fingerPrint():
	def __init__(self) :
		self.state_connect = "Khong"
		try:
			
			led = DigitalInOut(board.D13)
			led.direction = Direction.OUTPUT
			port = find_usb_serial_ports()
			print("Port: ", port)
			self.uart = serial.Serial(f"/dev/{port}", baudrate=57600, timeout=3)
			self.finger = adafruit_fingerprint.Adafruit_Fingerprint(self.uart)
			self.state_connect = "Co"
		except Exception as e:
			print(e)
			self.state_connect = "Khong"
	
	def close_port(self):
		self.uart.close()

	
	def get_fingerprint(self):
					"""Get a finger print image, template it, and see if it matches!"""
					try:
						if self.state_connect == "Co":
							print("Waiting for image...")
							
							while self.finger.get_image() != adafruit_fingerprint.OK:
								pass
							print("Templating...")
							if self.finger.image_2_tz(1) != adafruit_fingerprint.OK:
								return False
							print("Searching...")
							if self.finger.finger_search() != adafruit_fingerprint.OK:
								return False
							return True
						else:
							return self.state_connect
					except:
						return "Khong"

	# pylint: disable=too-many-branches
	def get_fingerprint_detail(self):
					"""Get a finger print image, template it, and see if it matches!
					This time, print out each error instead of just returning on failure"""
					
					if self.state_connect == "Co":
						print("Getting image...", end="")
						i = self.finger.get_image()
						if i == adafruit_fingerprint.OK:
							print("Image taken")
							
						else:
							if i == adafruit_fingerprint.NOFINGER:
								print("No finger detected")
							elif i == adafruit_fingerprint.IMAGEFAIL:
								print("Imaging error")
							else:
								print("Other error")
							return False

						print("Templating...", end="")
						i = self.finger.image_2_tz(1)
						if i == adafruit_fingerprint.OK:
							print("Templated")
						else:
							if i == adafruit_fingerprint.IMAGEMESS:
								print("Image too messy")
							elif i == adafruit_fingerprint.FEATUREFAIL:
								print("Could not identify features")
							elif i == adafruit_fingerprint.INVALIDIMAGE:
								print("Image invalid")
							else:
								print("Other error")
							return False

						print("Searching...", end="")
						i = self.finger.finger_fast_search()
						# pylint: disable=no-else-return
						# This block needs to be refactored when it can be tested.
						if i == adafruit_fingerprint.OK:
							print("Found fingerprint!")
							return True
						else:
							if i == adafruit_fingerprint.NOTFOUND:
								print("No match found")
							else:
								print("Other error")
							return False
					else:
						return self.state_connect

	# pylint: disable=too-many-statements
	def enroll_finger(self,location): # Bắt đầu scan vân tAY
					"""Take a 2 finger images and template it, then store in 'location'"""
					if self.state_connect == "Co":
						for fingerimg in range(1, 3):
							if fingerimg == 1:
								print("Place finger on sensor...", end="")
							else:
								print("Place same finger again...", end="")

							while True:
								i = self.finger.get_image()
								if i == adafruit_fingerprint.OK:
									print("Image taken")
									break
								if i == adafruit_fingerprint.NOFINGER:
									print(".", end="")
								elif i == adafruit_fingerprint.IMAGEFAIL:
									print("Imaging error")
									return False
								else:
									print("Other error")
									return False

							print("Templating...", end="")
							i = self.finger.image_2_tz(fingerimg)
							if i == adafruit_fingerprint.OK:
								print("Templated")
							else:
								if i == adafruit_fingerprint.IMAGEMESS:
									print("Image too messy")
								elif i == adafruit_fingerprint.FEATUREFAIL:
									print("Could not identify features")
								elif i == adafruit_fingerprint.INVALIDIMAGE:
									print("Image invalid")
								else:
									print("Other error")
								return False

							if fingerimg == 1:
								print("Remove finger")
								time.sleep(1)
								while i != adafruit_fingerprint.NOFINGER:
									i = self.finger.get_image()

						print("Creating model...", end="")
						i = self.finger.create_model()
						if i == adafruit_fingerprint.OK:
							print("Created")
						else:
							if i == adafruit_fingerprint.ENROLLMISMATCH:
								print("Prints did not match")
							else:
								print("Other error")
							return False

						print("Storing model #%d..." % location, end="")
						i = self.finger.store_model(location)
						if i == adafruit_fingerprint.OK:
							print("Stored")
						else:
							if i == adafruit_fingerprint.BADLOCATION:
								print("Bad storage location")
							elif i == adafruit_fingerprint.FLASHERR:
								print("Flash storage error")
							else:
								print("Other error")
							return False

						return True
					else:
						return self.state_connect


	##################################################

	def get_num(self,list_van_tay):
		"""Use input() to get a valid number from 1 to 127. Retry till success!"""
		
		if type(list_van_tay) == int:
			new_id = list_van_tay
			return new_id
		elif type(list_van_tay) == list:
			if len(list_van_tay) > 0:
				last_id = len(list_van_tay)
				new_id = last_id + 1
				if new_id > 127:
					return 'Day dung luong-vui long xoa bot'
					
				return new_id
			else:
				new_id = 1
				return new_id
			
	def save_van_tay(self,list_van_tay):
					check_van_tay = self.get_fingerprint()
					if check_van_tay == True:
						print('Da ton tai van tay')
						return False
					elif check_van_tay == "Khong":
						return "Khong"
					else:
						state_enroll = self.enroll_finger(self.get_num(list_van_tay))
						
						if state_enroll == True:
							# Đẩy idNew vân tay lên firebase với email
							# put lại id lên
							return True
						else:
							print("Lỗi enroll")
							return False
				
			
			
	def find_van_tay(self):
		
					state_find_van_tay = self.get_fingerprint()
					if state_find_van_tay == True:
						id = self.finger.finger_id
						print("ID: ", id)
						print(type(id))
						
						# Check id trong list_van_tay lấy về từ firebase
						
						return id, True
					elif state_find_van_tay == "Khong":
						return 0, "Khong"  

					else:
						return 0, False
			
	def remove_van_tay(self):
					check_van_tay = self.get_fingerprint()
					if check_van_tay == True:
						id_van_tay = self.finger.finger_id
						if self.finger.delete_model(id_van_tay) == adafruit_fingerprint.OK:
							
							# xóa bỏ id của người dùng đó ở firebase
							
							print("Deleted!")
							return True
						
						else:
							print("Failed to delete")
							return False
					
					elif check_van_tay == "Khong":
						return "Khong"
					else:
						print('Fail to delete')
						return False
            



