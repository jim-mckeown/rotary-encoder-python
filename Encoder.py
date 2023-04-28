"""
Created on Sun Feb 14 12:26:06 2021

@author: Jim McKeown
"""

import math
import numpy as np
import cv2

activeSize = 100
threshold = 180

cap = cv2.VideoCapture(0)

# Check success
if not cap.isOpened():
    raise Exception("Could not open video device")
# Set properties. Each returns === True on success (i.e. correct resolution)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def normalize(rawAngle):
    if rawAngle >= 360.0:
        return rawAngle - 360.0
    if rawAngle < 0.0:
        return rawAngle + 360.0
    return rawAngle


# main loop
while(True):
    # Capture a frame
    ret, frame = cap.read()
    
    # convert color to grey-scale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # active area is activeSize x activeSize at center of captured image
    height, width, depth = frame.shape
    centerX = int(width / 2)
    centerY = int(height / 2)        
    Xul = int(centerX - (activeSize / 2)) # 170 @ 300 activeSize
    Yul = int(centerY - (activeSize / 2)) # 90 @ 300 activeSize
    Xlr = int(centerX + (activeSize / 2)) # 469 @ 300 activeSize
    Ylr = int(centerY + (activeSize / 2)) # 379 @ 300 activeSize   

    #draw green square around active area
    cv2.rectangle(frame, pt1=(Xul,Yul), pt2=(Xlr,Ylr), color=(0,255,0), thickness=1)
    #draw green crosshairs
    cv2.line(frame, pt1=(0, centerY), pt2=(Xul, centerY), color=(0,255,0), thickness=1)
    cv2.line(frame, pt1=(centerX, 0), pt2=(centerX, Yul), color=(0,255,0), thickness=1)
    cv2.line(frame, pt1=(Xlr, centerY), pt2=(width -1, centerY), color=(0,255,0), thickness=1)
    cv2.line(frame, pt1=(centerX, Ylr), pt2=(centerX, height - 1), color=(0,255,0), thickness=1)
    
    # slice the active area from grey-scale image
    active = gray[Yul+1:Ylr, Xul+1:Xlr]
    # convert active area to binary
    (thresh, active) = cv2.threshold(active, threshold, 255, cv2.THRESH_BINARY)

    # create empty arrays to hold edge data
    siVHtL = np.empty(shape = [0,2], dtype = float)    
    siVLtH = np.empty(shape = [0,2], dtype = float) 
    siHHtL = np.empty(shape = [0,2], dtype = float)    
    siHLtH = np.empty(shape = [0,2], dtype = float) 

    # vertical scan top to bottom
    for x in range(activeSize - 1):
        lastPixel = -1
        currentLineHtL = np.empty(shape = [0,2], dtype = float)
        currentLineLtH = np.empty(shape = [0,2], dtype = float)
        for y in range(activeSize - 1):
            # detect high to low transition
            currentPixel = active[y,x]
            if lastPixel == 255 and currentPixel == 0:
                # add coordinates to vertical high to low array (045-315)
                currentLineHtL = np.concatenate((currentLineHtL,(np.array([float(x), float(0-y)], ndmin=2))))
            if lastPixel == 0 and currentPixel == 255:
                # add coordinates to vertical low to high array (135-225)
                currentLineLtH = np.concatenate((currentLineLtH,(np.array([float(x), float(0-y)], ndmin=2))))
            lastPixel = currentPixel
        if currentLineHtL.shape[0] == 1:
            siVHtL = np.vstack((siVHtL, currentLineHtL))
        if currentLineLtH.shape[0] == 1:
            siVLtH = np.vstack((siVLtH, currentLineLtH))


    # horizontal scan left to right
    for y in range(activeSize - 1):
        lastPixel = -1
        currentLineHtL = np.empty(shape = [0,2], dtype = float)
        currentLineLtH = np.empty(shape = [0,2], dtype = float)        
        for x in range(activeSize - 1):
            # detect high to low transition
            currentPixel = active[y,x]
            if lastPixel == 255 and currentPixel == 0:
                # add coordinates to horizontal high to low array (225-315)
                currentLineHtL = np.concatenate((currentLineHtL,(np.array([float(x), float(y)], ndmin=2))))
            if lastPixel == 0 and currentPixel == 255:
                # add coordinates to vertical low to high array (045-135)
                currentLineLtH = np.concatenate((currentLineLtH,(np.array([float(x), float(y)], ndmin=2))))
            lastPixel = currentPixel
        if currentLineHtL.shape[0] == 1:
            siHHtL = np.vstack((siHHtL, currentLineHtL))
        if currentLineLtH.shape[0] == 1:
            siHLtH = np.vstack((siHLtH, currentLineLtH))

    # find longest line of data and calculate slope and y-intercept
    angle = 0.0
    sector = ""
    if siVHtL.shape >= siVLtH.shape and siVHtL.shape >= siHLtH.shape and siVHtL.shape >= siHHtL.shape:
        model = np.polyfit(siVHtL[:,0],siVHtL[:,1],1)
        angle = normalize(math.degrees(math.atan(model[0])))
        sector = "315 - 045"
    if siVLtH.shape > siVHtL.shape and siVLtH.shape >= siHLtH.shape and siVLtH.shape >= siHHtL.shape:
        model = np.polyfit(siVLtH[:,0],siVLtH[:,1],1)
        angle = normalize(math.degrees(math.atan(model[0])) + 180.0)
        sector = "135 - 225"
    if siHHtL.shape > siHLtH.shape and siHHtL.shape > siVLtH.shape and siHHtL.shape > siVHtL.shape:
        model = np.polyfit(siHHtL[:,1],siHHtL[:,0],1)
        angle = normalize(math.degrees(math.atan(model[0])) + 90.0)
        sector = "045 - 135"
    if siHLtH.shape > siHHtL.shape and siHLtH.shape >= siVLtH.shape and siHLtH.shape >= siVHtL.shape:
        model = np.polyfit(siHLtH[:,1],siHLtH[:,0],1)
        angle = normalize(math.degrees(math.atan(model[0])) + 270.0)
        sector = "225 - 315"
    print(sector, angle)
    
    # Display the resulting frame
    cv2.imshow('Rotary Encoder', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()


























