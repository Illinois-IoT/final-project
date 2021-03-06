from picamera.array import PiRGBArray
from picamera import PiCamera
import pygame
import datetime
import imutils
import time
import cv2

camera = PiCamera()
camera.resolution = (640, 480)
#camera.framerate = 32
raw_capture = PiRGBArray(camera, size=(640, 480))
time.sleep(1)
last_frame = None

pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.mixer.init()
pygame.mixer.music.load("arcade.wav")

min_area = 15

for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
    image = frame.array
    raw_capture.truncate()
    raw_capture.seek(0)
    
    maybe_motion_text = "Not Detected"
    if image is None:
        break

    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray,(21,21),0)

    if last_frame is None:
        last_frame = gray
        continue
        
    frame_delta = cv2.absdiff(last_frame,gray)
    thresh = cv2.threshold(frame_delta, 25,255,cv2.THRESH_BINARY)[1]
    
    thresh = cv2.dilate(thresh,None,iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    
    last_frame = gray
    
    for c in cnts:
        if cv2.contourArea(c) < min_area:
            continue
        (x,y,w,h) = cv2.boundingRect(c)
        cv2.rectangle(image,(x,y),(x+w,y+h), (0,255,0),2)
        maybe_motion_text = "Detected"
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()
        
        
    cv2.putText(image, "Motion: {}".format(maybe_motion_text), (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255),2)
    cv2.putText(image, datetime.datetime.now().strftime("%A %d %B %Y %I: %M: %S%p"), (10,image.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.35,(0,0,255),1)
        
    cv2.imshow("Feed", image)
    cv2.imshow("Threshold", thresh)
    cv2.imshow("Frame Delta", frame_delta)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cv2.destroyAllWindows()
