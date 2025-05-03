# It helps in identifying the faces 
import cv2, sys, numpy, os 

def face_recognition():
    size = 4
    haar_file = 'haarcascade_frontalface_default.xml' # Classifier used to detect faces
    datasets = 'datasets'
    
    # Part 1: Create fisherRecognizer 
    print('Recognizing Face Please Be in sufficient Lights...') 
    
    # Create a list of images and a list of corresponding names 
    (images, labels, names, id) = ([], [], {}, 0) 

    print("Current Working Directory:", os.getcwd())
    print("Files in datasets:", os.path.exists('datasets'))


    for (subdirs, dirs, files) in os.walk(datasets): 
        print("Subdirs:", subdirs)
        print("Dirs:", dirs)
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
    (images, labels) = [numpy.array(lis) for lis in [images, labels]]

    # OpenCV trains a model from the images 
    # NOTE FOR OpenCV2: remove '.face' 
    model = cv2.face.LBPHFaceRecognizer_create() # Model used to train the dataset
    model.train(images, labels) 

    # Part 2: Use fisherRecognizer on camera stream 
    face_cascade = cv2.CascadeClassifier(haar_file) 
    webcam = cv2.VideoCapture(0) 
    while True: 
        (_, im) = webcam.read() 
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) 
        faces = face_cascade.detectMultiScale(gray, 1.3, 5) # Here is where they identify faces

        for (x, y, w, h) in faces: # For each face in the sea of faces do the following... 
            cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2) 
            face = gray[y:y + h, x:x + w] 
            face_resize = cv2.resize(face, (width, height)) 
            
            # Try to recognize the face 
            prediction = model.predict(face_resize) 
            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 3) 
    
            if prediction[1]<70: # The lower the value, the more cofident the model in the prediction
                cv2.putText(im, '% s - %.0f' % 
                            (names[prediction[0]], prediction[1]), (x-10, y-10),  
                            cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
            else: 
                cv2.putText(im, 'not recognized: '+ str(prediction[1]),  
                            (x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0)) 
    
        cv2.imshow('FutureBanking', im) 
        
        key = cv2.waitKey(10) 
        if key == 27: 
            break