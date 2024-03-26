import cv2
import sqlite3
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
conn = sqlite3.connect("people.db")
while True:
    success, img
    cv2.imshow("Face Attendence", img)
    cv2.waitKey(1)




""" ROADMAP
TODO
we should prepare 3 py files:
face_taker.py --> opens camera and takes 10 picture with organized names and puts it in user_data folder
face_train --> it should train itself according to user_data folder and save it
face_recognizer --> this will be our main py file that recognize face and opens the lock

After these changes done we should connect these three files so it can run automatise structure

may we connect a database and edit face_taker and face_train according this so we can store more information other than user's picture

may we try on raspberry pi for the control lock and edit face_recognizer according to use pins on rp

may we connect an actual lock system to visualise our application

may we consider to deploy our application and create endpoints so any device with camera that connect at the same server can use without any installation or further work 

"""