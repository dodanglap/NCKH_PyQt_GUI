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
firebase = firebase.FirebaseApplication('https://fir-firebase-2eb50-default-rtdb.asia-southeast1.firebasedatabase.app', None)


led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

try:

    # If using with a computer such as Linux/RaspberryPi, Mac, Windows with USB/serial converter:
    import serial
    uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=3)

    # If using with Linux/Raspberry Pi and hardware UART:
    #import serial
    #uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

    finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
except:
    messagebox.showwarning("Lỗi", "Chưa có cảm biến vân tay")
    pass
##################################################


def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image...")
    
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Searching...")
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True


# pylint: disable=too-many-branches
def get_fingerprint_detail():
    """Get a finger print image, template it, and see if it matches!
    This time, print out each error instead of just returning on failure"""
    print("Getting image...", end="")
    i = finger.get_image()
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
    i = finger.image_2_tz(1)
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
    i = finger.finger_fast_search()
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


# pylint: disable=too-many-statements
def enroll_finger(location): # Bắt đầu scan vân tay
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="")
        else:
            print("Place same finger again...", end="")

        while True:
            i = finger.get_image()
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
        i = finger.image_2_tz(fingerimg)
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
                i = finger.get_image()

    print("Creating model...", end="")
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print("Storing model #%d..." % location, end="")
    i = finger.store_model(location)
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


##################################################


def get_num(list_van_tay):
    """Use input() to get a valid number from 1 to 127. Retry till success!"""
    
    
    if len(list_van_tay) > 0:
        last_id = len(list_van_tay)
        new_id = last_id + 1
        if new_id > 127:
            return 'Day dung luong-vui long xoa bot'
            
        return new_id
    else:
        new_id = 1
        return new_id
        
def save_van_tay(list_van_tay):
    check_van_tay = get_fingerprint()
    if check_van_tay == True:
        print('Da ton tai van tay')
        return False
    else:
					state_enroll = enroll_finger(get_num(list_van_tay))
					
					if state_enroll == True:
						# Đẩy idNew vân tay lên firebase với email
						# put lại id lên
						return True
					else:
						print("Lỗi enroll")
						return False
			
        
        
def find_van_tay(list_van_tay):
    state_find_van_tay = get_fingerprint()
    if state_find_van_tay == True:
        id = finger.finger_id
        
        # Check id trong list_van_tay lấy về từ firebase
        
        if id in list_van_tay :
            return True
        return False

    else:
        return False
        
def remove_van_tay(list_van_tay):
    check_van_tay = get_fingerprint()
    if check_van_tay == True:
        id_van_tay = finger.finger_id
        if finger.delete_model(id_van_tay) == adafruit_fingerprint.OK:
            
            # xóa bỏ id của người dùng đó ở firebase
            
            print("Deleted!")
            return True
        
        else:
            print("Failed to delete")
            return False

    else:
        print('Fail to delete')
        return False
            


