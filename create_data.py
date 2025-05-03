# Creating database 
# It captures images and stores them in datasets 
# folder under the folder name of sub_data 
import cv2, sys, numpy, os, time, keyboard, mysql.connector
import helper.HandTrackingModule as htm
from helper.sql_connector import sql_connector

haar_file = './helper/haarcascade_frontalface_default.xml'
numberOfImages = 50 # Number of images to be taken for facial recognition

def add_user(sub_data):
	global numberOfImages
	mydb = sql_connector()
	db = mydb.cursor(dictionary=True)

	sub_data = sub_data.strip()
	username = sub_data

	if sub_data is None or sub_data == "":
		return 2 # To indicate that there was no username inputted

	# All the faces data will be 
	# present this folder 
	folder_name = "datasets"

	if not os.path.exists(folder_name):
		os.makedirs(folder_name) # If there is no 'dataset' folder, create one

	datasets = folder_name

	# These are sub data sets of folder, 
	# for my faces I've used my name you can 
	# change the label here 
	#sub_data = 'tr'	

	path = os.path.join(datasets, sub_data) 

	if not os.path.isdir(path): 
		print("Creating User...")
		os.mkdir(path)

	else:
		return 1 # To indicate that user already exists

	# defining the size of images 
	(width, height) = (130, 100)	 

	# '0' is used for default laptop webcam, 
	# if you've any other camera 
	# attached use '1' instead 
	face_cascade = cv2.CascadeClassifier(haar_file) 
	webcam = cv2.VideoCapture(0)

	print("Standby. Look at the camera. No need for facial expressions") 
	time.sleep(1)
	for i in range(1,4):
		print(str(i)+"...")
		time.sleep(1)

	########## PART 1: SAVING OF USER FACE ##########
	# The program loops until it has 30 images of the face. 
	count = 1
	while count <= numberOfImages: 
		(success, im) = webcam.read() 

		if not success:
			print("Error: Failed to capture image")
			break

		gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) 
		faces = face_cascade.detectMultiScale(gray, 1.3, 4) 
		
		if len(faces) == 0: # If no face is detected
			print("***Please ensure you are detectable (i.e. Ensure no harsh light, Clear Background, Clear Face with no accessories***)")
			time.sleep(1)

		else:
			for (x, y, w, h) in faces: 
				cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2) 
				face = gray[y:y + h, x:x + w] 
				face_resize = cv2.resize(face, (width, height)) 
				writeStatus = cv2.imwrite('% s/% s.png' % (path, count), face_resize) 
				
				if writeStatus is True:
					print(f"Image {count} taken and saved.")
				else:
					print(f"Image {count} count not be taken or saved.")

			count += 1

		cv2.imshow("Creating User", im)
		key = cv2.waitKey(50) # The value here is very important as '1' would utimately mean its only giving your cpu 1 second to have identifed a face, capture and save the image into your folder 
		
		if key == 27: 
			webcam.release()
			cv2.destroyAllWindows()
			break

	cv2.destroyWindow("Creating User")

	########## PART 2: SAVING OF USER HAND GESTURE ##########
	# TO DO: Save user hand gesture into database
	print("Standby your hand gesture for future login.")
	time.sleep(0.5)
	print("Remember this exact hand gesture!")
	time.sleep(1)
	for i in range(1,4):
		print(str(i)+"...")
		time.sleep(1)

	# Initialize the hand detector
	detector = htm.handDetector(detectionCon=0.75)
	tipsIds = [4, 8, 12, 16, 20]
	fingers = []
	prev_fingers = [] 
	count = 0 # Counter for number of times the user holds the same gesture for # If user holds the same gesture for 5s long, count should be 5
	
	while True:
		success, img = webcam.read()  # Capture frame-by-frame
		if not success:
			print("Error: Failed to capture image")
			break

		img = detector.findHands(img)  # Process the image with hand detector
		lmlist = detector.findPosition(img, draw=False)

		if len(lmlist) != 0: # If we manage to get the position of the joints, find the finger tips. Refer to https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker for the image of the joint numbering
			fingers.clear()
			# 1. Do identification for thumb: The thumb needs special identification cause it is very hard to identify if it is above or below its joint. Easier to identify if it is closed or open through identifying whether it is to the left or right of its joint
			# As you can tell by the if statement below, through using the axis as the condition, we can tell that this is right-hand user biased!
			if lmlist[tipsIds[0]][1] < lmlist[tipsIds[0]-1][1]: # Notice that we are using the x (as we are using [1] instead of [2]) axis for the thumb to identify if it is opened or closed
				fingers.append(1) # If the finger is open, append a 1 to represent that. Each index in the finger will correspond to a finger (i.e. index 1 - Index Finger, index 2 - Middle Finger ...)

			else:
				fingers.append(0)

			# 2. Do identification for other fingers
			for id in range(1,5): 
				if lmlist[tipsIds[id]][2] < lmlist[tipsIds[id]-2][2]: # This condition checks whether or not a finger is opened or close. Recall that the origin of an axis in OpenCV is at the top left. As such, if a finger tip is above its joint (i.e. a finger is open), the position of the finger tip will be lower than that of its joint.
					fingers.append(1) # If the finger is open, append a 1 to represent that. Each index in the finger will correspond to a finger (i.e. index 1 - Index Finger, index 2 - Middle Finger ...)

				else:
					fingers.append(0)

			if fingers != prev_fingers:
				print("Different gesture recognised, changing...")
				prev_fingers = fingers.copy()
				count = 0

			elif fingers == prev_fingers:
				print("Same gesture recognised, saving...")
				print(fingers)
				count+=1

				if count == 5:
					print("Gesture confirmed!")
					break

			#print(fingers)

		else: # Unable to identfy joints
			print("Unable to indetify joints")
			
		cv2.imshow("Create User Gesture", img)  # Display the image with detected hands
		
		# Exit the loop if the ESC key is pressed
		if cv2.waitKey(1000) & 0xFF == 27:  # ESC key
			break
	
	path = os.path.join(path, 'user_handGesture.txt')

	# Save the data into a text file
	with open(path, 'w') as file:
		file.write(username + "\n" + str(fingers))

	# Save the data into sql
	insert_query = 	"""
					INSERT INTO users (username, thumb, index_f, middle_f, ring_f, pinky_f)
					VALUES (%s, %s, %s, %s, %s, %s)
					"""
	data = (username, fingers[0], fingers[1], fingers[2], fingers[3], fingers[4])
	
	try:
		db.execute(insert_query, data)
		mydb.commit()
		print("File created and text written. Data saved")

	except mysql.connector.Error as e:
		print("Saving of data to database failed: ", str(e))

	db.close()
	mydb.close()

	webcam.release()
	cv2.destroyAllWindows()
	cv2.waitKey(1)
	return 0
