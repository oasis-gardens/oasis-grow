#---------------------------------------------------------------------------------------
#Manages Camera Timing & Image transmission
#---------------------------------------------------------------------------------------
import sys
import signal
from typing import Type

#set proper path for modules
sys.path.append('/home/pi/oasis-grow')

#import libraries
import time
from imaging import noir_ndvi

import rusty_pipes
from utils import concurrent_state as cs
from utils import error_handler as err
from networking import db_tools as dbt

resource_name = "camera"

'''Here's the calling code
camera_process = rusty_pipes.Open(['python3', '/home/pi/oasis-grow/imaging/camera.py', cs.structs["hardware_config"]["camera_settings"]["picture_frequency"]]) #If running, then skips. If idle then restarts.
'''

def take_picture(image_path):
    if cs.structs["hardware_config"]["camera_settings"]["awb_mode"] == "on":
        #take picture and save to standard location: libcamera-still -e png -o test.png
        still = rusty_pipes.Open(["raspistill", "-e", "jpg",  "-o", str(image_path)]) #snap: call the camera. "-w", "1920", "-h", "1080",
        still.wait()
    else:
        still = rusty_pipes.Open(["raspistill", "-e", "jpg",  "-o", str(image_path), "-awb", "off", "-awbg", cs.structs["hardware_config"]["camera_settings"]["awb_red"] + "," + cs.structs["hardware_config"]["camera_settings"]["awb_blue"]]) #snap: call the camera. "-w", "1920", "-h", "1080",
        still.wait()
    
    exit_status = still.exit_code()
    return exit_status

def save_to_feed(image_path):
    #timestamp image
    timestamp = time.time()
    #move timestamped image into feed
    save_most_recent = rusty_pipes.Open(["cp", str(image_path), "/home/pi/oasis-grow/data_out/image_feed/image_at_" + str(timestamp)+'.jpg'])
    save_most_recent.wait()

def send_image(path):
    #send new image to firebase
    cs.load_state()
    user, db, storage = dbt.initialize_user(cs.structs["access_config"]["refresh_token"])
    dbt.store_file(user, storage, path, cs.structs["access_config"]["device_name"], "image.jpg")
    print("Sent image")

    #tell firebase that there is a new image
    dbt.patch_firebase(cs.structs["access_config"], "image_sent", "1")
    print("Firebase has an image in waiting")

def clean_up(*args):
    cs.safety.unlock(cs.lock_filepath, resource_name)
    sys.exit()

#define a function to actuate element
def actuate(interval, nosleep = False): #amount of time between shots in minutes
    cs.load_state()

    exit_status = take_picture('/home/pi/oasis-grow/data_out/image.jpg')
    
    if exit_status == 0:

        if cs.structs["feature_toggles"]["ndvi"] == "1":
            noir_ndvi.convert_image('/home/pi/oasis-grow/data_out/image.jpg')

        if cs.structs["feature_toggles"]["save_images"] == "1":
            save_to_feed('/home/pi/oasis-grow/data_out/image.jpg')

        if cs.structs["device_state"]["connected"] == "1":
            #send new image to firebase
            send_image('/home/pi/oasis-grow/data_out/image.jpg')

        if nosleep == True:
            return
        else:
            time.sleep(float(interval)*60) #once the physical resource itself is done being used, we can free it
                                        #not a big deal if someone actuates again while the main spawn is waiting
                                        #so long as they aren't doing so with malicious intent (would need DB or root access, make sure to turn off SSH or change your password)
    else:
        print("Was not able to take picture!")
        time.sleep(5)
        clean_up()


if __name__ == '__main__':
    cs.check_lock(resource_name) #no hardware acquisition happens on import
    signal.signal(signal.SIGTERM,clean_up) #so we can check for the lock in __main__
    
    try:    
        actuate(str(sys.argv[1]))
    except KeyboardInterrupt:
        print("Camera was interrupted.")
    except TypeError:
        print("Tried do image stuff without an image. Is your camera properly set up?")
        time.sleep(10)
    except Exception:
        print("Camera encountered an error!")
        print(err.full_stack())
    finally:
        clean_up()

        


