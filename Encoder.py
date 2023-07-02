"""
Created on Sun Feb 14 12:26:06 2021
Updated on Sun Jul 02 13:45:00 2023
@author: Jim McKeown
"""

import cv2
import socket
import extract_angle

# Connect to the server with `telnet localhost 5000`.

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(False)
server.bind(('localhost', 5000))
server.listen(5)

connections = []

activeSize = 50
threshold = 180
N_min = 30

cap = cv2.VideoCapture(0)

# Check success
if not cap.isOpened():
    raise Exception("Could not open video device")
# Set properties. Each returns === True on success (i.e. correct resolution)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

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
    active = gray[Yul:Ylr, Xul:Xlr]
    # convert active area to binary
    (thresh, active) = cv2.threshold(active, threshold, 255, cv2.THRESH_BINARY)

    # get angle from active area array
    angle, std_err, sector = extract_angle.getAngle(active, N_min)    
    print(angle, std_err, sector)
    
    # Display the resulting frame
    cv2.imshow('Rotary Encoder', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    # Send numerical result to telnet client
    try:
        connection, address = server.accept()
        connection.setblocking(False)
        connections.append(connection)
    except BlockingIOError:
        pass

    for connection in connections:
        try:
            command = connection.recv(4096)
        except BlockingIOError:
            continue
            for connection in connections:
                #connection.send(bytes(('%3.1f\n\r' % angle),'UTF-8'))
                connection.send(bytes('{:0>5.1f}\n\r'.format(command), 'UTF-8'))
        except BrokenPipeError:
            continue        

# When everything done, release the capture
server.close()
cap.release()
cv2.destroyAllWindows()

























