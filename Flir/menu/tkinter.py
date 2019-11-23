
import cv2
import imutils
import numpy as np
import shutil
import os
import requests
import glob
import math
import random
import os.path
import json
import warnings
import datetime	

 
 
# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
#cap_grey     = cv2.VideoCapture(1)
cap_normal   = cv2.VideoCapture(2)
cap_color =    cv2.VideoCapture(3)

cv2.namedWindow('image_normal', cv2.WINDOW_NORMAL)
#cv2.namedWindow('image_grey',   cv2.WINDOW_NORMAL)
cv2.namedWindow('image_color',  cv2.WINDOW_NORMAL)
#cv2.namedWindow('image_edges',  cv2.WINDOW_NORMAL)


cv2.resizeWindow('image_normal', 500,300)
#cv2.resizeWindow('image_grey',   500,300)
cv2.resizeWindow('image_color',  500,300)
#cv2.resizeWindow('image_edges',  500,300)


cv2.moveWindow("image_normal",  0, 36)
#cv2.moveWindow("image_grey",    0, 366)
cv2.moveWindow("image_color",   0, 700)
#cv2.moveWindow("image_edges",   1600, 900)




###################### OBTENEMOS LOS FRAMES DE CADA DEVICE ########################
if (cap_normal.isOpened()== False): 
  print("Error abriendo el dev/video2")
  
#if (cap_grey.isOpened()== False): 
#  print("Error abriendo el dev/video1")
  
if (cap_color.isOpened()== False): 
  print("Error abriendo el dev/video3")
  

 
# Read until video is completed
while(cap_normal.isOpened() & cap_color.isOpened()):
  
  # Capture frame-by-frame
  ret_normal, frame_normal  = cap_normal.read()
  #ret_grey,   frame_grey    =   cap_grey.read()
  ret_color,  frame_color   =  cap_color.read()
  
  #edges = cv2.Canny(frame_color,100,200)
  #canny = cv2.Canny(np.mean(frame_color, axis=2).astype(np.uint8), 100, 200)
  #color_output = np.bitwise_or(frame_color, canny[:,:,np.newaxis])
  
  

 

  if ret_normal == True & ret_color == True:

	cv2.imshow('image_normal',frame_normal)
	#cv2.imshow('image_grey',    frame_grey)
	cv2.imshow('image_color',  frame_color)
	#cv2.imshow('image_edges', color_output)
	
	#cv2.imwrite("LastPic.png",frame_normal)
	#cv2.imwrite("Last_Frames/Last_Pic_Grey.png",frame_grey)
	#cv2.imwrite("Last_Pic_Color.png",frame_color)
	#print("imagenes guardadas")

 
 
    # Press Q on keyboard to  exit
	if cv2.waitKey(25) & 0xFF == ord('q'):
		#Descomentar esto para guardar el ulitmo frame del stream
		cv2.imwrite("Last_Frames/LastPic.png",frame_normal)
		#cv2.imwrite("Last_Frames/Last_Pic_Grey.png",frame_grey)
		cv2.imwrite("Last_Frames/Last_Pic_Color.png",frame_color)
		#cv2.imwrite("Last_Frames/Last_Pic_Color_Edges.png",color_output)


		break
 
  # Break the loop
  else: 
	print("No esta mostrando bien los frames")
	break
 
 
 
# When everything done, release the video capture object
cap_normal.release()
#cap_grey.release()
cap_color.release()

 
# Closes all the frames
cv2.destroyAllWindows()
