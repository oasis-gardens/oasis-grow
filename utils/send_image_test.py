import sys

#set proper path for modules
sys.path.append('/home/pi/oasis-grow')
sys.path.append('/home/pi/oasis-grow/imaging')
sys.path.append('/usr/lib/python37.zip')
sys.path.append('/usr/lib/python3.7')
sys.path.append('/usr/lib/python3.7/lib-dynload')
sys.path.append('/home/pi/.local/lib/python3.7/site-packages')
sys.path.append('/usr/local/lib/python3.7/dist-packages')
sys.path.append('/usr/lib/python3/dist-packages')

import cameraElement as cam

def send_image_test():
    cam.stately.load_state()
    user, db, storage = cam.initialize_user(cam.stately.access_config["refresh_token"])
    cam.send_image(user, storage, "/home/pi/image.jpg")
    return

if __name__ == '__main__':  
    send_image_test()
  
