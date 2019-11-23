
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


from ibm_watson import VisualRecognitionV3
from Tkinter import *
from PIL import Image, ImageTk
import Tkinter
from Tkinter import Tk, StringVar, Frame, Pack
import ttk



warnings.filterwarnings("ignore")
NUMBER_OF_DIVISIONS = 4
POWER_AI_VISION_API_CLASSI_URL = "https://localhost/powerai-vision/api/dlapis/2aba33ce-3716-471b-8618-2c9bf53afd2b"
POWER_AI_VISION_API_URL = "https://localhost/powerai-vision/api/dlapis/cc9e7c64-85ea-4358-a22a-1891b547f8b0"

print("---------------DEMO DE VISUAL INSIGHTS----------------\n\nPulsa p para usar la deteccion de objectos termicos\nPulsa e para division en cuadriculas y deteccion de objetos\nPulsa q para salir de la demo\n")



###  START OF FUNCTIONS  ###

 
def RecognizeObject_VisualRecog(imagen,contador):
	
	cv2.imwrite("celda.png",imagen)	
	
	# VISUAL RECOGNITION API
	visual_recognition = VisualRecognitionV3('2019-06-21',iam_apikey='YuGs3PFCMTaCCJvSs-5nvrSZ5Knnzl3kuRiTEE7qGnMz')
	faces = visual_recognition.detect_faces("celda.png").get_result()
	print(json.dumps(faces, indent=2))
	
	#Contador solo se usa para avanzar con la demo haciendo como que se ha encontrado una tecla
	if(contador == 5):
		print("Se ha encontrado una tuberia en el contador: "+str(contador)+"\n\n")
		return True
		
		
		
def Draw_object_detected(imagen_normal,xmin,xmax,ymin,ymax):

			
		my_file = 'Power/deteccion.png'
		if os.path.isfile(my_file):
			
			img_global = cv2.imread('Power/deteccion.png')
			img_termic = cv2.imread('Power/request_pos.png')
			img_global[ymin:ymin+img_termic.shape[0], xmin:xmin+img_termic.shape[1]] = img_termic		
			cv2.imwrite("Power/deteccion.png",img_global)	
				
		else:
			
			img_global = cv2.imread('Power/global_s.png',0)
			img_termic = cv2.imread('Power/request_pos.png',0)
			img_global[ymin:ymin+img_termic.shape[0], xmin:xmin+img_termic.shape[1]] = img_termic
		
			cv2.imwrite("Power/deteccion.png",img_global)


		cv2.namedWindow('final_image', cv2.WINDOW_NORMAL)
		cv2.resizeWindow('final_image', 600,800)
		cv2.moveWindow("final_image",   500, 400)
		cv2.imshow('final_image',     img_global)


	
	
		
		
def RecognizeObject_PowerAIVision(imagen,frame_color):
	
	#BORRAMOS EL CONTENIDO DEL DIRECTORIO BLOCKS
	folder = 'Power/' 
	for the_file in os.listdir(folder): 
		file_path = os.path.join(folder, the_file) 
		try: 
			if os.path.isfile(file_path): 
				os.unlink(file_path) 
			#elif os.path.isdir(file_path): shutil.rmtree(file_path) 
		except Exception as e: 
			print(e) 
	#FIN DEL BORRADO
	

	cv2.imwrite("Power/global.png",imagen)
	img = Image.open("Power/global.png")
	img = img.resize((160,120), Image.ANTIALIAS)
	img.save("Power/global_s.png") 


	print('enviando la imagen...')
	#POWER AI VISION API
	s = requests.Session()
	with open('Power/global_s.png', 'rb') as f:
        # WARNING! verify=False is here to allow an untrusted cert!
		r = s.post(POWER_AI_VISION_API_URL,
                   files={'files': ('Power/global_s.png', f)},
                   verify=False)

	rc        =  r.status_code
	resp_json =  json.loads(r.text)
	print(resp_json)
	values     = resp_json.get('classified')
	
	if not values:
		print("1 - VisualInsights no ha encontrado ninguna confianza en la captura tomada\n2 - Fallo en la API del servidor  ")
	
	else:
		
		for objeto in range(0, len(values)):
			
			confidence = values[objeto]['confidence']
			
			ymax       = values[objeto]['ymax']
			ymin       = values[objeto]['ymin']
			
			xmax       = values[objeto]['xmax']
			xmin       = values[objeto]['xmin']
		
		
			if(confidence > 0.5):
				print('\nObjeto encontrado con una confianza del: '+str(confidence)+'\nextrayendo imagen termica\n')
				print('xmin-> '+str(xmin)+'\nxmax-> '+str(xmax)+'\nymin-> '+str(ymin)+'\nymax-> '+str(ymax)+'\n\n')
				#print('image-> '+type(imagen))
				img = Image.open("Power/global_s.png")
				#cropped_top = img.crop[xmin:xmax , ymin:ymax]
				cropped_top = img.crop((xmin,ymin,xmax,ymax))
				cropped_top.save("Power/recortada_normal_"+str(objeto)+".png") 

				#cv2.imwrite("Power/Img_Cropped_Normal.png",cropped_top)
				#print('Imagen normal recortada')
				
				if(ObtainThermicObject_PowerAI_Vision(frame_color,xmin,xmax,ymin,ymax,objeto,imagen)):
					print("imagen enviada para sacar la termica")
					
			else:
				print('Objeto encontrado con una confianza del: '+str(confidence)+'\nConfianza escasa, pruebe de nuevo\n\n')
			
	
	
	
def ObtainThermicObject_Cell(frame_color,numero):
	
	frame_color = frame_color[20:120 ,20:120]
	cv2.imwrite("Problem/Img_General_Color.png",frame_color)
	heights, widths = frame_color.shape[:2]
	print("height: "+str(heights))
	print("width:  "+ str(widths))

	jump_heights = heights / NUMBER_OF_DIVISIONS
	jump_widths =  widths  / NUMBER_OF_DIVISIONS
	contador = 0

	for x in range(0,widths,jump_widths):
		for y in range(0,widths,jump_widths):
			contador+=1
			cropped_top = frame_color[x:x+jump_widths , y:y+jump_widths]
			cv2.imwrite("Problem/Img_"+str(contador)+".png",cropped_top)
			
			print("buscando contador: "+str(contador))
			if(contador == numero):
				print("Encontrado! \nGuardando imagen....")
				cv2.imwrite("Problem/Img_Target_Color.png",cropped_top)
				break
		if(contador == numero):
			break

 
def ObtainThermicObject_PowerAI_Vision(frame_color, xmin, xmax, ymin, ymax,objeto,frame_normal):
	
	cv2.imwrite("Power/Img_General_Color.png",frame_color)
	cropped_top = frame_color[xmin:xmax , ymin:ymax]
	cv2.imwrite("Power/recortada_color_"+str(objeto)+".png",cropped_top)
	cv2.imwrite("Power/request.png",cropped_top)

	
	#aqui hacemos el request al clasificador
	s = requests.Session()
	with open('Power/request.png', 'rb') as f:
        # WARNING! verify=False is here to allow an untrusted cert!
		r = s.post(	POWER_AI_VISION_API_CLASSI_URL,
                   files={'files': ('Power/request.png', f)},
                   verify=False)

	rc        =  r.status_code
	resp_json =  json.loads(r.text)
	#print(resp_json)
	values     = resp_json.get('classified')
	
	if not values:
		print("No se ha clasificado correctamente")
	
	else:
		print(values)
		key = values.keys()
		value = values.values()
		#print(key,value)
		
		if 'Positivo' in values:
			if value > 0.8:
				cv2.imwrite("Power/request_pos.png",cropped_top)
				print('Imagen termica encontrada, en proceso de ser dibujada...')
				#cv2.imwrite("Power/termic.png",cropped_top)
				Draw_object_detected(frame_normal,xmin,xmax,ymin,ymax)
		else:
			print("...")
		

			print('Proceso terminado y guardado en la carpeta Power')
 	return True

 
 
# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
cap_grey     = cv2.VideoCapture(1)
cap_normal   = cv2.VideoCapture(2)
cap_color =    cv2.VideoCapture(3)

cv2.namedWindow('image_normal', cv2.WINDOW_NORMAL)
cv2.namedWindow('image_grey',   cv2.WINDOW_NORMAL)
cv2.namedWindow('image_color',  cv2.WINDOW_NORMAL)
cv2.namedWindow('image_edges',  cv2.WINDOW_NORMAL)


cv2.resizeWindow('image_normal', 500,400)
cv2.resizeWindow('image_grey',   500,400)
cv2.resizeWindow('image_color',  500,400)
cv2.resizeWindow('image_edges',  500,400)


cv2.moveWindow("image_normal",  300, 200)
cv2.moveWindow("image_grey",    810, 200)
cv2.moveWindow("image_color",   300, 700)
cv2.moveWindow("image_edges",   810, 700)




# DEFINIMOS LOS PARAMETROS PARA GRABAR, DESCOMENTAR LINEAS:16,17,44 PARA VOLVER A GRABAR
#fourcc = cv2.cv.CV_FOURCC(*'XVID')
#out = cv2.VideoWriter('ejemplo.avi',fourcc, 20.0, (640,480))

 

###################### OBTENEMOS LOS FRAMES DE CADA DEVICE ########################
if (cap_normal.isOpened()== False): 
  print("Error abriendo el dev/video2")
  
if (cap_grey.isOpened()== False): 
  print("Error abriendo el dev/video1")
  
if (cap_color.isOpened()== False): 
  print("Error abriendo el dev/video3")
  

  
  


 
# Read until video is completed
while(cap_normal.isOpened() & cap_grey.isOpened() & cap_color.isOpened()):
  
  # Capture frame-by-frame
  ret_normal, frame_normal  = cap_normal.read()
  ret_grey,   frame_grey    =   cap_grey.read()
  ret_color,  frame_color   =  cap_color.read()
  
  #edges = cv2.Canny(frame_color,100,200)
  canny = cv2.Canny(np.mean(frame_color, axis=2).astype(np.uint8), 100, 200)
  color_output = np.bitwise_or(frame_color, canny[:,:,np.newaxis])
  
  

 

  if ret_normal == True & ret_grey == True & ret_color == True:

	cv2.imshow('image_normal',frame_normal)
	cv2.imshow('image_grey',    frame_grey)
	cv2.imshow('image_color',  frame_color)
	cv2.imshow('image_edges', color_output)
	
	#cv2.imwrite("Last_Frames/LastPic.png",frame_normal)
	#cv2.imwrite("Last_Frames/Last_Pic_Color.png",frame_color)
	#print("displaying...")


    #Si queremos guardar el video descomentamos la linea de abajo
    #out.write(frame)
    
	if cv2.waitKey(25) & 0xFF == ord('e'):
		
		#obtenemos por pantalla el numero de divisiones que queremos del frame
		divisiones = input("Indica el numero de divisiones que quieres\n\n --> 4 columnas \n\n --> 5 columnas \n\n --> 6 columnas \n\n*enter para ser 12 celdas por defecto*: ")
		if(divisiones != None and divisiones < 7 and divisiones > 3):
			NUMBER_OF_DIVISIONS = int(divisiones)
			print("Numero de divisiones: ", divisiones)  
		else:
			NUMBER_OF_DIVISIONS = 4
			print("Numero de divisiones: ", divisiones)  


		
		
		#BORRAMOS EL CONTENIDO DEL DIRECTORIO BLOCKS
		folder = 'Blocks/' 
		for the_file in os.listdir(folder): 
			file_path = os.path.join(folder, the_file) 
			try: 
				if os.path.isfile(file_path): 
					os.unlink(file_path) 
				#elif os.path.isdir(file_path): shutil.rmtree(file_path) 
			except Exception as e: 
				print(e) 
		#FIN DEL BORRADO	
					
		#Cut the normal frame to fix with the grey one
		height, width = frame_normal.shape[:2]
		#print("el height de la imagen es:  " + str(height))
		#print("el width  de la imagen es:  " +  str(width))
				
		
		#frame_normal = frame_normal[50:1080 ,50:1440]
		frame_normal = frame_normal[60:1080 ,60:1080]


		cv2.imwrite("Img_Cropped.png",frame_normal)

		
		## TERMINAMOS DE HACER EL RECORTE DE LA IMAGEN NORMAL
		
		height, width = frame_normal.shape[:2]
		
		jump_height = height / NUMBER_OF_DIVISIONS
		jump_width =  width  / NUMBER_OF_DIVISIONS
		contador = 0
		
		##Draw the lines in the original frame and put yes/no labels in each frame....
		frame_drawed = frame_normal
		font = cv2.FONT_HERSHEY_SIMPLEX


		for x in range(0,width,jump_width):
			for y in range(0,width,jump_width):
				contador+=1
				cropped_top = frame_normal[x:x+jump_width , y:y+jump_width]
				cv2.line(frame_drawed,(y,0),(y+jump_width,0),(0,255,0),4)	
				cv2.line(frame_drawed,(0,y),(0,y+jump_width),(0,255,0),4)	
				cv2.line(frame_drawed,(y+jump_width,0),(y+jump_width,width),(0,255,0), 4)	
				cv2.line(frame_drawed,(0,y+jump_width),(width,y+jump_width),(0,255,0), 4)	


				print("estudianto celda: "+str(contador-1))			
				if(contador <= (NUMBER_OF_DIVISIONS*NUMBER_OF_DIVISIONS)):
					if(RecognizeObject_VisualRecog(cropped_top,contador)):
						cv2.imwrite("Problem/Img_Target_Normal.png",cropped_top)
						ObtainThermicObject_Cell(frame_color,contador)
						print("Hay una tuberia y su imagen termica se ha guardado...\n\n")
						cv2.putText(cropped_top,'YES',(20,150), font, 0.7,(255,255,255),2)

					else:
						cv2.putText(cropped_top,'NO' ,(20,150), font, 0.7,(255,255,255),2)
				if(contador == NUMBER_OF_DIVISIONS*NUMBER_OF_DIVISIONS):
					print("\n\n--------------Procesamiento de la imgen terminada---------------------------\n\n--------------Pulse *e* para volver a analizar otro frame-------------------\n\n--------------Pulse *qq* para terminar la ejecucion de la demo--------------\n\n")
					break
						
				cv2.imwrite("Blocks/Img_"+str(contador)+".png",cropped_top)
		cv2.imwrite("Summary_Frame/division.png",frame_drawed)





	if cv2.waitKey(25) & 0xFF == ord('p'):
		print('Llamando al Visual Insigths para el reconocimiento...')
		
		#frame_normal = frame_normal[0:160 ,0:120]
		#frame_color = frame_color[20:120 ,20:120]

		if(RecognizeObject_PowerAIVision(frame_normal,frame_color)):
			print('Fin del procesamiento del frame')
			


 
	if cv2.waitKey(25) & 0xFF == ord('m'):
		numero = random.randrange(1000)
		print("guardando imagen...")
		cv2.imwrite("Modelo1/"+str(numero)+".png",frame_normal)

    
 
    # Press Q on keyboard to  exit
	if cv2.waitKey(25) & 0xFF == ord('q'):
		#Descomentar esto para guardar el ulitmo frame del stream
		cv2.imwrite("Last_Frames/LastPic.png",frame_normal)
		cv2.imwrite("Last_Frames/Last_Pic_Grey.png",frame_grey)
		cv2.imwrite("Last_Frames/Last_Pic_Color.png",frame_color)
		cv2.imwrite("Last_Frames/Last_Pic_Color_Edges.png",color_output)


		#Descomentar para extraer los valores de los pixeles del ultimo frame en csv
		#f = open ('ValoresPixeles.txt','w')
		#for x in range(0, frame.shape[0]):
		#	for y in range(0, frame.shape[1]):
		#		f.write(str(frame[x][y]) + ",")
		#f.close()

		break
 
  # Break the loop
  else: 
	print("No esta mostrando bien los frames")
	break
 
 
 
# When everything done, release the video capture object
cap_normal.release()
cap_grey.release()
cap_color.release()

 
# Closes all the frames
cv2.destroyAllWindows()
