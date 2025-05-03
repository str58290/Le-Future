# It helps in identifying the faces 
import cv2, sys, numpy, os, mysql.connector
import helper.HandTrackingModule as htm
from helper.sql_connector import sql_connector

prediction_threshold = 65 # Threshold for positive identification of face. The lower the more stringent the prediction must be in order for the positive identification of the person
not_recog_str = "Not Recognised" # Standardised string to label faces not recognised
successful_count = 10 # Number of times that user needs to be successfully recognised in order for successful login (i.e. prevention of accidental/"lucky" logins)

def face_finger_combined():

    mydb = sql_connector()
    db = mydb.cursor(dictionary=True)

    global prediction_threshold
    #==========INITIALIZATION FOR FACE==========#
    size = 4
    haar_file = './helper/haarcascade_frontalface_default.xml' # Classifier used to detect faces
    datasets = 'datasets'
    person = ''

    (subdirs, dirs, files) = next(os.walk(datasets))
    print("Subdirs:", subdirs)
    print("Dirs:", dirs)

    if len(dirs) == 0: # If there are no folders of users (i.e. no users)
        return 0 # 0 Indicates problem in this function cause we are returning ID at the end of a successful login (i.e. a positive int is returned upon successful login)
    
    # Part 1: Create fisherRecognizer 
    print('Recognizing Face Please Be in sufficient Lights...') 
    
    # Create a list of images and a list of corresponding names 
    (images, labels, names, id) = ([], [], {}, 0) 

    print("Current Working Directory:", os.getcwd())
    print("Files in datasets:", os.path.exists('datasets'))


    for (subdirs, dirs, files) in os.walk(datasets): 
        for subdir in dirs: 
            names[id] = subdir 
            subjectpath = os.path.join(datasets, subdir) 

            print("subjectpath: "+subjectpath)

            for filename in os.listdir(subjectpath): 
                path = os.path.join(subjectpath, filename)  # Use os.path.join for better path handling
                print("path: "+path)
                img = cv2.imread(path, 0)  # Read in grayscale

                if img is not None:
                    images.append(img)
                    labels.append(id)

                else:
                    print(f"Failed to load image: {path}")
            id += 1

    (width, height) = (130, 100) 
    
    # Create a Numpy array from the two lists above 
    (images, labels) = [numpy. array(lis) for lis in [images, labels]]

    # OpenCV trains a model from the images 
    # NOTE FOR OpenCV2: remove '.face' 
    model = cv2.face.LBPHFaceRecognizer_create() # Model used to train the dataset
    model.train(images, labels) 

    #==========INITIALIZATION FOR FINGER==========#
    detector = htm.handDetector(detectionCon=0.75)
    tipsIds = [4, 8, 12, 16, 20]
    fingers = []

    # Part 2: Use fisherRecognizer on camera stream 
    face_cascade = cv2.CascadeClassifier(haar_file) 
    cap = cv2.VideoCapture(0)

    successful_counter_helper = 0
    user_id = None
    prev_user_id = None

    while successful_counter_helper != successful_count: 
        #==========INITIALIZE CAMERA FOR FACE AND FINGER MODULES TO USE==========#
        (success, im) = cap.read() 

        if not success:
            print("Error: Failed to capture image")
            break

        #==========IDENTIFICATION OF FACE==========#
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) 
        faces = face_cascade.detectMultiScale(gray, 1.3, 5) # Here is where they identify faces

        if len(faces) != 0: # If we manage to identify a face...
            for (x, y, w, h) in faces: # For each face in the sea of faces do the following... 
                cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Draw a rectangle around the face
                face = gray[y:y + h, x:x + w] 
                face_resize = cv2.resize(face, (width, height)) 
                
                # Try to recognize the face 
                prediction = model.predict(face_resize) 
                cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 3) 
        
                if prediction[1]<prediction_threshold: # The lower the value, the more cofident the model in the prediction (i.e. prediction[1] will be lower)
                    cv2.putText(im, '% s - %.0f' % 
                                (names[prediction[0]], prediction[1]), (x-10, y-10),  
                                cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
                    person = names[prediction[0]]

                else: 
                    cv2.putText(im, not_recog_str + str(prediction[1]),  
                                (x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0)) 
                    person = not_recog_str
        
        else: # Otherwise, keep person as None to help ensure that both face and fingers MUST be present for log in
            person = None

        #==========IDENTIFICATION OF FINGERS==========#
        im = detector.findHands(im)  # Process the image with hand detector
        lmlist = detector.findPosition(im, draw=False)

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

            #print(fingers)

        else: # Unable to identfy joints, keep 'fingers' variable empty to help ensure that both face and fingers MUST be present for log in
            fingers.clear()
            print("Unable to indetify joints")

        print("Identification: " + str(person))
        print("Gesture: " + str(fingers))

        if len(fingers) != 0 and str(person) != not_recog_str:
            select_query = """
                            SELECT id FROM users 
                            WHERE username = %s AND thumb = %s AND index_f = %s AND middle_f = %s AND ring_f = %s AND pinky_f = %s
                            """
            data = (str(person), fingers[0], fingers[1], fingers[2], fingers[3], fingers[4])
            db.execute(select_query, data)
            result = db.fetchone()  # Fetch the first matching row
            print("Result:" + str(result))

            if result:
                print("User id: " + str(result["id"]))
                user_id = result["id"]

                if user_id == prev_user_id:
                    successful_counter_helper += 1
                
                elif user_id != prev_user_id:
                    prev_user_id = user_id
                    successful_counter_helper = 0
            
            else:
                print("Login unsuccessful...")        

        cv2.imshow('FutureBanking', im) 
        
        key = cv2.waitKey(50) 
        if key == 27: 
            break

    cap.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)

    db.close()
    mydb.close()

    return user_id

#face_finger_combined()