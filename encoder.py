#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import cv2
import threading
import extract_angle


class encoder:
    
    def __init__(self):
        self.activeSize = 50
        self.threshold = 180
        self.N_min = 30
        
        self.angle = 0.0
        self.std_err = 0.0
        self.sector = ""
        
        
        self.okToRun = True
        
        
        cv2.destroyAllWindows() 
        
        self.cap = cv2.VideoCapture(0)
        print("Opening camera.", end="")
        while not self.cap.isOpened():
            print(".", end="")
            time.sleep(0.5)
        
        print("")
        
        # Check success
        if not self.cap.isOpened():
            raise Exception("Could not open video device")
        # Set properties. Each returns === True on success (i.e. correct resolution)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = False # Daemonize thread or not
        thread.start()        # Start the execution                
        
    
    def run(self): # main loop
        while(self.okToRun):
            # Capture a frame
            
            ret, frame = self.cap.read()
            
            # convert color to grey-scale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
            # active area is activeSize x activeSize at center of captured image
            height, width, depth = frame.shape
            centerX = int(width / 2)
            centerY = int(height / 2)        
            Xul = int(centerX - (self.activeSize / 2)) # 170 @ 300 activeSize
            Yul = int(centerY - (self.activeSize / 2)) # 90 @ 300 activeSize
            Xlr = int(centerX + (self.activeSize / 2)) # 469 @ 300 activeSize
            Ylr = int(centerY + (self.activeSize / 2)) # 379 @ 300 activeSize   
        
            #draw green square around active area
            cv2.rectangle(frame, pt1=(Xul,Yul), pt2=(Xlr,Ylr), color=(0,255,0), thickness=1)
            #draw green crosshairs
            cv2.line(frame, pt1=(0, centerY), pt2=(Xul, centerY), color=(0,255,0), thickness=1)
            cv2.line(frame, pt1=(centerX, 0), pt2=(centerX, Yul), color=(0,255,0), thickness=1)
            cv2.line(frame, pt1=(Xlr, centerY), pt2=(width -1, centerY), color=(0,255,0), thickness=1)
            cv2.line(frame, pt1=(centerX, Ylr), pt2=(centerX, height - 1), color=(0,255,0), thickness=1)
            
            # slice the active area from grey-scale image
            active = gray[Yul:Ylr, Xul:Xlr]
            # convert active area to binary
            (thresh, active) = cv2.threshold(active, self.threshold, 255, cv2.THRESH_BINARY)
                    
            # get angle from active area array
            self.angle, self.std_err, self.sector = extract_angle.getAngle(active, self.N_min)    
            # print(self.angle, self.std_err, self.sector)
            
            # Display the resulting frame
            cv2.imshow('Rotary Encoder', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        # When everything done, release the capture
        #server.close()
        self.cap.release()
        cv2.destroyAllWindows() 
        print("ending " + __name__)           
    
    def setOkToRun(self, state):
        self.okToRun = state 

    def getAngle(self):
        return self.angle
    
    def getStdErr(self):
        return self.std_err

    def getSector(self):
        return self.sector
    
    def setActiveSize(self, activeSize):
        self.activeSize = activeSize
        
    def getActiveSize(self):
        return self.activeSize
    
    def setThreshold(self, threshold):
        self.threshold = threshold

    def setNmin(self, N_min):
        self.N_min = N_min
    
if __name__ == '__main__':
    e = encoder()
    e.run()    
                

    






















