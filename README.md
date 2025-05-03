# Le Future
#### Video Demo:  <https://youtu.be/IN2VcUilkQE>
#### Description:
Observing that some laptops still rely on slightly older technology, advanced biometric logins that require newer technology (like "TrueDepth" cameras) are not possible for these minorities. As such, I thought of an innovative way to go about the problem, to ensure that these minorities do not compromise their security while doing high-security activities (e.g. login to internet banking, home security cameras and personal profiles).

Organisations can seek to use this technology to ensure customer satisfaction and security to customers slightly behind in technology.

In addition, this project was also created to bring about a futuristic way of logging in to an account using purely biometrics. Biometrical login methods are a lot safer than the conventional 'username' and 'password' way of logging in. However, it is not foolproof. Therefore, in order to make it more secure, instead of using only 1 biometrical data to log in (i.e. Face), why not use 2? This project introduces a new biometrical way of logging in: The use of a user's face and a specific hand gesture of the user's choice.

## Section #1: Pre-requisites
### To set up virtual machine and reqirements
1. Upon receiving this project folder, you will realise that this folder contains a python environment
2. Ensure that your cmd line/terminal window is in the '*CS50*' folder 
3. Next run the following to first create a virtual environment called '.venv':

    **For both Windows and Mac:** 

        python -m venv .venv

4. Activate the virtual environment next:

    **For Command Prompt:**

        .venv\Scripts\activate

    **For PowerShell:**
    
        .\.venv\Scripts\Activate

    **For Git Bash or WSL:**
    
        source .venv/bin/activate

4. Next run the following to download all the requirements needed for this project into your virutal environment:
        
        pip install -r requirements.txt

### To set up database
1. Ensure that you have mysql community server installed in your local computer (else watch a Youtube video to help you with it)

2. Create a database called 'le_future'

        CREATE DATABASE le_future;

3. Then, enter the database you just created

        USE le_future;

4. Configure ***'sql_connector.py'*** to connect to the sql database containing the tables. The program can be found in the 'helper' folder

5. Create the tables listed in **'Section #2'** before moving on

### To create admin account for program
1. Run the ***admin_creation.py*** program under the same 'helper' folder

2. Create admin account as instructed

## Section #2: Database and Tables creation
**USER DATA BASE:**

To store user biometric login details

    CREATE TABLE users (
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        thumb INTEGER NOT NULL,
        index_f INTEGER NOT NULL,
        middle_f INTEGER NOT NULL,
        ring_f INTEGER NOT NULL,
        pinky_f INTEGER NOT NULL
    );

**ADMIN DATA BASE:**

To store admin login credentials for the admin purposes (i.e. Adding of new user)

    CREATE TABLE admin (
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) 
    );

Once all is done, you are now free to use the program! Run the following in your terminal to use the program:

    python main.py

Below is a detailed breakdown of the project. You may want to take a look if you're looking to configure it to your liking.

## More about C50_FinalProject.py
### Feature 1: "Add User" - add_new_user()
### Description: 

In this function, in order for the user to add new users, they first have to
login to admin. Conventionally, they will be required to enter a username and password
and only upon the right credentials entered will they be allowed to access admin rights of adding 
a new user. Point to note is that the admin password saved in the database has been hashed and salted using
bycrypt. 

When adding a new user, users are first required to provide their face for facial recognition.
In providing thier face, 30 images of their face will be captured for the facial recognition model
to recognise them. After which, users will be expected to hold a hand gesture, with which they will
use to log in to their account along with their face, for 5 seconds in order for their hand gesture to be saved
into the database. The hand gesture recognition algorithm is rather simple as it only make use of the user's 
finger tips (i.e. no other joint points) to create what's so-called a "hand gesture". As such, if future improvements were to be made,
I would recommend to make the hand gesture recognition more robust and stringent through the use of more joint
points and a certain algorithm to computate the forming/identification of a hand gesture.

### Important libraries used:
*1. mysql*

- To retrieve admin login details
- To add new users and their details (their username and log in hand gesture)
- To update/add user facial data to improve user facial recognition

*2. bcrypt*

- To hash password to match with hashed password stored in admin database
- Hashed password stored in the admin database is salted with the salt generator provided by library
- NOTE: We have to encode user's input before hashing it with bcrypt as
        bcrypt only take in byte strings as its argument.

*3. create_data.py*

- Self written library where the main bulk of creating a user comes in
- Program will identify the user's face, take 30 images of his/her face (if face no face identified, program will wait out)
    - After which, these images will be saved into a local folder with the user's name as folder name
    - This folder(s) in the dataset will be fed to the face recognition model
- After saving the user's face, the program will then ask user to hold a hand gesture, of which they will log in via.
    - The identification of a hand gesture will provide, ultimately, return a list with 5 values (that will be saved to the 'fingers' list variable)
    - 'fingers' list variable essentially just tells which fingers are up and which ones are down (i.e. index 0 - thumb: if 1 means up 0 means down)
    - We are able to tell whether or not a user has held the hand gesture up for 5 seconds by comparing the old hand gesture 
        current 'fingers' variable to the previous fingers variable stored in "previous_fingers". Through the use of cv2.waitKey(1000)
        we are able to time the 5 seconds perfectly, though it will bring a slightly laggy
        video capture. Though laggy, it also means that more time can be allocated to properly
        identifying the fingers of the user and other backend computation.
- Lastly, after both face and hand gesture has been created, we save the user name and hand gesture positionings to SQL for the saving of data


### Feature 2: "Log in" - log_in()
### Description:

In this function, users log in to their own personal accounts through face and hand gesture recognition.

### Important libraries used:

*1. face_finger_combined*

- This library runs a face identification model, following which, a face recognition model that identifies saved faces stored in the folder "datasets > (USERNAME)"
- After a successful face recognition of a user, the user's name will be noted in the variable 'person'
- Note that we can change how stringent we want our model to be in order for the successful identification of a user.
    - Just change the value of the global variable 'prediction_threshold' at the top. The lower the value (i.e. the closer to 0), the more stringent. There is no "highest value" for the prediction confidence score but the lowest goes to only 0 (a perfect match - meaning to say your user 
    to look EXACLTY the same as when he/she took their "create user" photos needs). A good range would be 50-70 for correctly recognised faces, while 100-150 for mismatched faces.
- The hand gesture model will then run after the unsuccessful/successful identification of a face.
- Once a hand has been recognised, the finger tips will be taken and used for checking whether or not the user is using the correct hand gesture to login (provided that the user is already correctly identified)
- Upon successful facial and hand gesture recognition, the data of the username and fingertips (whether it is opened or closed) will be sent to the database for verification. If the user with the hand gesture is found in the database, what is returned is the user's id matched to that user. This is then returned back to our main CS50_FinalProject's 'log_in()' function, of which we can use to display the user's web page accordingly

- The nit-grits of the function:
    - A face and hand MUST be present in order for a log in attempt to occur
    - In addition the right face and corresponding hand gesture must be present for at least x number of 'successful_count' (see 'successful_count' variable)
    - This is because our face recognition model is working on only with only 30 images to train. As such, it may mis-recognise users, and with just the corresponding hand gesture, users may  either be logged in to NOT their account or a non-user may 'hack' the system to log in to another user's account
    - Note that the higher the successful_count, the longer it will take for users to login (i.e. they will have to hold the hand gesture longer)
