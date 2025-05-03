import threading, bcrypt, mysql.connector, os, keyboard, time
from face_finger_combined import face_finger_combined
from create_data import add_user
from helper.sql_connector import sql_connector

mydb = sql_connector()
db = mydb.cursor(dictionary=True)  # Enable dictionary cursor
load_code_firstTime = True

def main():
    global load_code_firstTime
    
    if load_code_firstTime:
        clear_screen()
        load_code_firstTime = False

    print("Future Banking:")
    print("1. Add/Edit User")
    print("2. Log In")
    select = input("Select Usage: ")

    while True:
        if (select == '1'):
            add_new_user()
            break

        elif (select == '2'):
            log_in()
            break

        else:
            select = input("Select Usage: ")
    
def add_new_user():
    print("=========ADMINISTRATOR LOGIN=========")
    print("-> Press 'TAB' to login for administrator rights")
    print("-> Press 'ESC' to go back to main menu")

    while True:  
        if keyboard.is_pressed('esc'):
            clear_screen()
            main()

        if keyboard.is_pressed('tab'):
            keyboard.send('backspace') # Need to send backspace as the tab character from keyboardis_pressed() is sent to the very next input() buffer
            user_inp_name = input("Username: ")
            user_inp_pw = input("Password: ")
            user_inp_pw = user_inp_pw.encode()

            db.execute("SELECT username, password FROM admin WHERE username=%s", (user_inp_name,))
            result = db.fetchall()
            
            if not result: # If no such user exists in the admin database...
                clear_screen("Username is incorrect.")
                add_new_user()

            else:
                # Extract the password from the result tuple
                correct_username = result[0]['username']
                correct_password = result[0]['password']
                correct_password = correct_password.encode() # We need to encode the password first because bcrypt() works with byte strings and not pure strings

                # Check if the entered password matches the stored hash
                if user_inp_name == correct_username and bcrypt.checkpw(user_inp_pw, correct_password):
                    clear_screen()
                    print("Login Successful!")
                    print("=========ADD USER=========")
                    print("-> Press 'TAB' to input new user")
                    print("-> Press 'ESC' to go back to main menu") 

                    while True:
                        if keyboard.is_pressed('esc'):
                            clear_screen()
                            main()

                        if keyboard.is_pressed('tab'):
                            keyboard.send('backspace') # Need to send backspace as the tab character from keyboardis_pressed() is sent to the very next input() buffer
                            new_username = input("-> Enter New Username (no spaces): ").strip()
                            new_username = new_username.upper()
                            
                            if add_user(new_username) == 1:
                                clear_screen(new_username + "User Already Exists!")
                                print("-> Press 'TAB' to input new user")
                                print("-> Press 'ESC' to go back to main menu") 

                            elif add_user(new_username) == 2:
                                print("Please input a username!")
                                print("-> Press 'TAB' to input new user")
                                print("-> Press 'ESC' to go back to main menu") 

                            else:
                                clear_screen("########## NEW USER CREATED! ##########")
                                main()

                else:
                    print("Password is incorrect.")
                    add_new_user()
        
def log_in():
    print("=========USER LOGIN=========")
    print("-> Press 'ESC' to go back to main menu")
    value = face_finger_combined()
    print("debug: " + str(value))

    if value:
        clear_screen("Log in successful!")
        print("User ID: " + str(value))
        main()

    elif not value:
        clear_screen("No users in database. Please create a user first.")
        add_new_user()

#***************FUNCTIONS THAT HELP WITH THE AESTHETIC/FLOW OF PROGRAM***************
def clear_screen(append_line=""): # Clear Black Window for aesthetics
    if os.name == 'nt':  # For Windows
        os.system('cls')
        print(append_line)

    else:  # For macOS and Linux
        os.system('clear')
        print(append_line)

main()