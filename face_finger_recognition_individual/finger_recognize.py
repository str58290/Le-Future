import cv2
import os
import HandTrackingModule as htm

def finger_recognition():
    
    # Open the webcam
    cap = cv2.VideoCapture(0) 
    if not cap.isOpened():
        print("Error: Could not open camera")
        exit()

    # Initialize the hand detector
    detector = htm.handDetector(detectionCon=0.75)

    tipsIds = [4, 8, 12, 16, 20]

    while True:
        success, img = cap.read()  # Capture frame-by-frame
        if not success:
            print("Error: Failed to capture image")
            break

        img = detector.findHands(img)  # Process the image with hand detector
        lmlist = detector.findPosition(img, draw=False)

        if len(lmlist) != 0: # If we manage to get the position of the joints, find the finger tips. Refer to https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker for the image of the joint numbering
            fingers = []
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

            print(fingers)

        else: # Unable to identfy joints
            print("Unable to indetify joints")

        cv2.imshow("Create User Gesture", img)  # Display the image with detected hands
        
        # Exit the loop if the ESC key is pressed
        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break

    # Release the camera and close any OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

finger_recognition()
