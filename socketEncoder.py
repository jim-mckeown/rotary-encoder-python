#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import encoder # external custom class

commands = [["angle", "size", "thresh", "nmin"], 
            ["set", "get"]]


HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 5000  # Port to listen on (non-privileged ports are > 1023)


e = encoder.encoder()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
print("Waiting for connection...")
s.listen()
conn, addr = s.accept()
print(f"Connected by {addr}")
buffer = b''
try:
    while True:
        data = conn.recv(1)
        if not data:
            break
        buffer += data
        if buffer.decode().endswith("\r\n"):
            # parse buffer
            strBuffer = buffer.decode() # convert received bytes to a string
            strBuffer = strBuffer.removesuffix("\r\n") # strip off terminating cr, lf
            aryBuffer = strBuffer.split(",") # parse received string into string array
            if len(aryBuffer) > 0: # check for zero length array
                if aryBuffer[0] == commands[0][0]: # process command 0
                    if len(aryBuffer) == 1: 
                        
                        # process command 0 (angle) with no parameters:
                                                    
                        buffer = bytes(str(e.getAngle()), 'UTF-8') + b'\r\n'
                        conn.sendall(buffer)
                        
                    if len(aryBuffer) == 2: 
                        
                        # process command 0 with 1 parameter
                        # angle can not be set so ignore this command
                        #buffer = b'Received cmmand 0 with paramater: ' + bytes(aryBuffer[1], 'UTF-8') + b'\r\n'
                        #conn.sendall(buffer)
                        pass
                    
                if aryBuffer[0] == commands[0][1]: # process command 1
                    if len(aryBuffer) == 1: 
                        
                        # process command 1 with no parameters
                        buffer = bytes(str(e.getActiveSize()), 'UTF-8') + b'\r\n'
                        conn.sendall(buffer)
                        
                    if len(aryBuffer) == 2: 
                        
                        # process command 1 with 1 parameter
                        e.setActiveSize(float(aryBuffer[1]))
                        buffer = bytes(str(e.getActiveSize()), 'UTF-8') + b'\r\n'
                        conn.sendall(buffer)
                        
            buffer = b'' #clear buffer after command is processed
finally: # close socket if any error is raised
    print("ending " + __name__)
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    e.setOkToRun(False)
    e = None






























