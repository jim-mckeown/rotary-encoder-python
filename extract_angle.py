#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 17 15:41:32 2023

@author: jmckeown
"""
import numpy as np
import random
import scipy
import math

def getRandomList(size): # Generate a random list with no repeats
    randomList = []
    for i in range(size):
        r = random.randint(0, size - 1)
        while r in randomList:
            r = random.randint(0, size - 1)
        randomList.append(r)
    return randomList

def normalize(rawAngle):
    if rawAngle >= 360.0:
        return rawAngle - 360.0
    if rawAngle < 0.0:
        return rawAngle + 360.0
    return rawAngle

def getAngle(active, N_min):
    angle = 0.0
    std_err = 0.0
    sector = ""
    
    activeSize, activeSize = active.shape
    # create empty arrays to hold edge data
    siVHtL = np.empty(shape = [0,2], dtype = float)    
    siVLtH = np.empty(shape = [0,2], dtype = float) 
    siHHtL = np.empty(shape = [0,2], dtype = float)    
    siHLtH = np.empty(shape = [0,2], dtype = float) 
    
    # Do one vertical and one horizontal scan, check for minum N and r_value. Stop scanning when there is a winner.    
    randomX = getRandomList(activeSize)
    randomY = getRandomList(activeSize)
    
    for i in range(activeSize):
    
        # vertical scan top to bottom
        x = randomX[i]
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
        y = randomY[i]
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
            
        # Check for a winner and calculate slope, std_err, angle, sector
        N, w = siVHtL.shape
        if N >= N_min:
            slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(siVHtL[:,0],siVHtL[:,1])
            angle = normalize(math.degrees(math.atan(slope)))
            sector = "315 - 045"            
            break
        N, w  = siVLtH.shape
        if  N >= N_min:
            slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(siVLtH[:,0],siVLtH[:,1])
            angle = normalize(math.degrees(math.atan(slope)) + 180.0)
            sector = "135 - 225"            
            break
        N, w = siHHtL.shape
        if N >= N_min:
            slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(siHHtL[:,1],siHHtL[:,0])
            angle = normalize(math.degrees(math.atan(slope)) + 90.0)
            sector = "045 - 135"            
            break
        N, w = siHLtH.shape
        if  N >= N_min:
            slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(siHLtH[:,1],siHLtH[:,0])
            angle = normalize(math.degrees(math.atan(slope)) + 270.0)
            sector = "225 - 315"            
            break

    return angle, std_err, sector
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        