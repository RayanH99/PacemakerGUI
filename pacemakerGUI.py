import tkinter as tk
from tkinter import messagebox
import os
import serial
import struct
import time

titleFont = ("Verdana", 12)


class GUI(tk.Tk):


    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (WelcomePage, LoginPage, RegisterPage, afterLogin):
            frame = F(container, self)

            self.frames[F] = frame
            
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(WelcomePage)


    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


class WelcomePage(tk.Frame):


    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        frame = tk.Frame(width = 50, height = 50)
        frame.pack()

        global userData
        userData = {}

        tk.Label(self, text=" ").pack()
        tk.Label(self, text=" ").pack()
        label = tk.Label(self, text = "Welcome to Group #23's Pacemaker User Interface!", font=titleFont)
        label.pack(padx=30, pady=10)
        tk.Label(self, text=" ").pack()

        button = tk.Button(self, text="Login", width=15, height=3, command=lambda: controller.show_frame(LoginPage))
        button.pack(padx=30, pady=10)

        button2 = tk.Button(self, text="Register", width=15, height=3, command=lambda: controller.show_frame(RegisterPage))
        button2.pack(padx=30, pady=10)


class LoginPage(tk.Frame):


    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller
        user = tk.StringVar()
        password = tk.StringVar()
        global userData
        global parameters
        global parameterRanges

        ## Storing 19 parameters
        parameters = ['Lower Rate Limit', 'Upper Rate Limit', 'Maximum Sensor Rate', 'Fixed AV Delay',
                      'Atrial Amplitude', 'Ventricular Amplitude', 'Atrial Pulse Width', 'Ventricular Pulse Width',
                      'Atrial Sensitivity', 'Ventricular Sensitivity', 'VRP', 'ARP', 'PVARP', 'Hysteresis',
                      'Rate Smoothing', 'Activity Threshold', 'Reaction Time', 'Response Factor', 'Recovery Time']

        
        ####################################
        ####### STORING RANGES OF PARAMETERS
        ####################################

        parameterRanges = ['30-50ppm (inc by 5ppm), 50-90ppm (inc by 1ppm), 90-175ppm (inc by 5ppm)', '50-175ppm (inc by 5ppm)', '50-175ppm (inc by 5ppm)', '70-300ms (inc by 10ms)',
                            'Off(0), 500-3200mV (inc by 100mV), 3500-7000mV (inc by 500mV)', 'Off(0), 500-3200mV (inc by 100mV), 3500-7000mV (inc by 500mV)',
                            '0.05ms, 0.1-1.9ms (inc by 0.1ms)', '0.05ms, 0.1-1.9ms (inc by 0.1ms)', '0.25, 0.5, 0.75, 1.0-10mV (inc by 0.5mV)', '0.25, 0.5, 0.75, 1.0-10mV (inc by 0.5mV)',
                            '150-500ms (inc by 10ms)', '150-500ms (inc by 10ms)', '150-500ms (inc by 10ms)', 'Off(0), 30-50ppm (inc by 5ppm), 50-90ppm (inc by 1ppm), 90-175ppm (inc by 5ppm)','Off(0), 3, 6, 9, 12, 15, 18, 21, 25', 'V-Low, Low, Med-Low, Med, Med-High, High, V-High', '10-50sec (inc by 10sec)', '1-16 (inc by 1)', '2-16min (inc by 1min)']

        tk.Label(self, text=" ").pack()
        tk.Label(self, text=" ").pack()
        label = tk.Label(self, text = "Enter your username and password!", font=titleFont)
        label.pack(padx=30, pady=10)
        
        tk.Label(self, text=" ").pack()
        tk.Label(self, text="Username:").pack()
        tk.Entry(self, textvariable=user).pack()
        tk.Label(self, text="Password:").pack()
        tk.Entry(self, show="*", textvariable=password).pack()
        tk.Label(self, text=" ").pack()

        button = tk.Button(self, text="Login", width=15, height=3, command=lambda: self.__Login__(user.get(), password.get()))
        button.pack(padx=30, pady=10)

        button2 = tk.Button(self, text="Register", width=15, height=3, command=lambda: controller.show_frame(RegisterPage))
        button2.pack(padx=30, pady=10)

        ## add next page ref


    def __Reference__(self):
        global userData
        global userOutput
        userOutput = ""

        if(not (os.stat("userData.txt").st_size == 0)):
            file = open("userData.txt", "r")
            for line in file.readlines():
                userCredential = line.split(" ")

                if(userCredential[0] == "\n"):
                    continue
                
                user = userCredential[0]
                password = userCredential[1].strip("\n")

                userData[user] = createUser(user, password) ##create user object to store in database

            file.close()

        return userData


    def __Login__(self, user, password):
        userData = self.__Reference__()
        if user in userData:
            if userData[user].getPassword() == password:
                global currentUser
                currentUser = user
                return self.nextPage(afterLogin) 
            else:
                messagebox.showwarning(password, "Invalid login credentials!")
        else:
            messagebox.showwarning("Error!", "Invalid login credentials!")


    def nextPage(self, next):
        self.controller.show_frame(next)


class createUser():
  
  
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.userOutput = ""

        # multiply each pacing mode by 8 to be able to store each of the desired parameters
        self.parameters = {}
        self.parameters['AOO'] = ['0']*19
        self.parameters['AAI'] = ['0']*19
        self.parameters['VOO'] = ['0']*19
        self.parameters['VVI'] = ['0']*19
        self.parameters['DOO'] = ['0']*19
        self.parameters['AOOR'] = ['0']*19
        self.parameters['AAIR'] = ['0']*19
        self.parameters['VOOR'] = ['0']*19
        self.parameters['VVIR'] = ['0']*19
        self.parameters['DOOR'] = ['0']*19


    def getUser(self):
        return self.user


    def getPassword(self):
        return self.password


    def getParam(self):
        return self.parameters


    def getUserOutput(self):
        return self.userOutput


class RegisterPage(tk.Frame):


    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller
        global userData
        user = tk.StringVar()
        password = tk.StringVar()

        tk.Label(self, text=" ").pack()
        tk.Label(self, text=" ").pack()
        label = tk.Label(self, text = "Register a username and password!", font=titleFont)
        label.pack(padx=30, pady=10)

        tk.Label(self, text=" ").pack()

        tk.Label(self, text="Username:").pack()
        tk.Entry(self, textvariable=user).pack()
        tk.Label(self, text="Password:").pack()
        tk.Entry(self, show="*", textvariable=password).pack()

        tk.Label(self, text=" ").pack()

        button = tk.Button(self, text="Register User", width=15, height=3, command=lambda: self.__RegisterUser__(user.get(), password.get()))
        button.pack(padx=30, pady=10)

        button2 = tk.Button(self, text="Return to welcome!", width=15, height=3, command=lambda: controller.show_frame(WelcomePage))
        button2.pack(padx=30, pady=10)


    def __RegisterUser__(self, user, password):
        global userData
        userID = user
        userPassword = password

        if(not user or not password):
            return
        
        with open("userData.txt") as file:
            numUsers = len(file.readlines())

        if(numUsers == 10):
            messagebox.showwarning("Error!", "Maximum of 10 pacemaker users reached!")
            return
        else:
            if(self.__isValidUser__(user, password)):
                if(user in userData and userData[user].getPassword() == password):
                    messagebox.showwarning("Error!", "User already exists in database, use a different name!")
                else:
                    file = open("userData.txt", "a")
                    file.write(userID + " " + userPassword + "\n")
                    file.close()
        
                    userData[user] = createUser(user, password)
                    
                    messagebox.showwarning("Success!", "User was successfully registered!")
                    self.controller.show_frame(WelcomePage)
                    return
            else:
                messagebox.showwarning("Error!", "Invalid login credentials!")
                return


    ## function checks if new user registered with a valid username and password by checking the type of characters used (only numbers and alphabet allowed)
    def __isValidUser__(self, user, password):
        for character in user:
            if not character.isalpha() and not character.isdigit():
                messagebox.showwarning("Error!", "Invalid username!")
                return False

        for character in password:
            if not character.isalpha() and not character.isdigit():
                messagebox.showwarning("Error!", "Invalid password!")
                return False

        return True


class afterLogin(tk.Frame):


    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        self.controller = controller
        global PacingModes
        PacingModes = { 
            'AOO': [1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'AAI': [1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
            'VOO': [1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'VVI': [1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0],
            'DOO': [1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'AOOR': [1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], 
            'AAIR': [1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],         
            'VOOR': [1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
            'VVIR': [1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1],
            'DOOR': [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
        }

        global dropOption
        dropOption = tk.StringVar()

        global dropList
        dropList = []

        global currentDropList
        currentDropList = []

        logoutButton = tk.Button(self, text="Logout", command=lambda: self.controller.show_frame(WelcomePage))
        logoutButton.grid(row=0,column=1, pady=20)

        paramsTitle = tk.Label(self, text="Parameters", font=("Verdana", 15))
        paramsTitle.grid(row=2, column=0)

        updateParams = tk.Button(self, text="Update Parameters", command=self.__updateParams__)
        updateParams.grid(row=2, column=1)

        modeTitle = tk.Label(self, text="Pacing Mode", font=("Verdana", 15))
        modeTitle.grid(row=3, column=0, pady=20)
        
        dropOption.set('   ')
        tk.OptionMenu(self, dropOption, *PacingModes.keys(), command=self.__List__).grid(row=3, column=1)


    def __otherList__(self, *args):
        global dropList

        mode = dropOption.get()
        rowIndex = 4

        if(dropList):
            for i in range(len(dropList)):
                dropList[i].grid_remove()
            dropList = []
        counter = 0

        for i in range(len(parameters)):
            if(PacingModes[mode][i] == 1):
                dropList.append(tk.Label(self, text=parameters[i]))
                dropList[counter].grid(row=rowIndex, column=0)

                counter += 1

                dropList.append(tk.Entry(self, textvariable=tk.StringVar()))
                dropList[counter].grid(row=rowIndex, column=1)

                counter += 1
                rowIndex += 1

    
        ####################################
        ####### ADDED MORE ERROR CHECKING FOR NEW PARAMETERS
        ####################################
    def __getParams__(self, *args):
        global validParameters
        validParameters = {
            'Lower Rate Limit': [str(x) for x in range(30, 55, 5)]+[str(x) for x in range(50, 90, 1)]+[str(x) for x in range(90, 180, 5)],
            'Upper Rate Limit': [str(x) for x in range(50, 180, 5)],
            'Maximum Sensor Rate': [str(x) for x in range(50, 180, 5)],
            'Fixed AV Delay': [str(x) for x in range(70, 300, 10)],
            'Atrial Amplitude': ['O']+[str(x) for x in range(500, 3300, 100)]+[str(x) for x in range(3500, 7500, 500)],
            'Ventricular Amplitude': ['O']+[str(x) for x in range(500, 3300, 100)]+[str(x) for x in range(3500, 7500, 500)],
            'Atrial Pulse Width': ['0.05']+[str(x*0.1) for x in range(1, 19, 1)],
            'Ventricular Pulse Width': ['0.05']+[str(x*0.1) for x in range(1, 19, 1)],
            'Atrial Sensitivity': ['0.25', '0.5', '0.75']+[str(x*0.1) for x in range(10, 105, 5)],
            'Ventricular Sensitivity': ['0.25', '0.5', '0.75']+[str(x*0.1) for x in range(10, 105, 5)],
            'VRP': [str(x) for x in range(150, 510, 10)],
            'ARP': [str(x) for x in range(150, 510, 10)],
            'PVARP': [str(x) for x in range(150, 510, 10)],
            'Hysteresis': ['0']+[str(x) for x in range(30, 55, 5)]+[str(x) for x in range(50, 90, 1)]+[str(x) for x in range(90, 180, 5)],
            'Rate Smoothing': ['0', '3', '6', '9', '12', '15', '18', '21', '25'],
            'Activity Threshold': ['V-Low', 'Low', 'Med-Low', 'Med', 'Med-High', 'High', 'V-High'],
            'Reaction Time': [str(x) for x in range(10, 60, 10)],
            'Response Factor': [str(x) for x in range(1, 17, 1)],
            'Recovery Time': [str(x) for x in range(2, 17, 1)]
        }

        mode = dropOption.get()
        
        
        ####################################
        ####### ADDED A WAY TO INFORM USER WHICH VALUE IS INCORRECT
        ####################################

        for i in range(1, len(dropList), 3):
            if(dropList[i].get() in validParameters[dropList[i-1]['text']]):
                userData[currentUser].parameters[mode][parameters.index(dropList[i-1]['text'])] = dropList[i].get()
                currentDropList[i].config(text=str(dropList[i].get()))
            else:
                messagebox.showwarning("Error!", "Invalid parameter value! Check: " + dropList[i-1].cget("text"))
                break


        ####################################
        ####### FUNCTION TO CONVERT ALL NUMS TO 8 BIT
        ####################################
    def __intConversion__(self, num, numOfBytes):
        if num == None:
            num = 0
        num = int(num)
        byte1 = (num & 0xff)
        byte2 = ((num >> 8) & 0xff)
        if (numOfBytes == 1):
            return [byte1]
        return [byte1, byte2]

    
        ####################################
        ####### ADDED SERIAL COMMUNICATION
        ####################################
    def __serialCommunication__(self, *args):
        ##########################################################################################################################################################
        ## CHANGE COM PORT HERE
        serialPacemaker = serial.Serial('COM3', 115200) ## default baudrate for serial communication is 115200

        print("Serial port has been opened!")

       ## time.sleep(2)

        selectedPacingMode = dropOption.get()
        arrayToSend = userData[currentUser].parameters[selectedPacingMode]
        tempMode = selectedPacingMode
        activity = arrayToSend[14]

        ACTIVITY_THRESHOLD = 0
        
        # set integer value for selected pacing mode
        if tempMode == "AOO":
            MODE = 1
        elif tempMode == "AAI":
            MODE = 2
        elif tempMode == "VOO":
            MODE = 3
        elif tempMode == "VVI":
            MODE = 4
        elif tempMode == "DOO":
            MODE = 5
        elif tempMode == "AOOR":
            MODE = 6
        elif tempMode == "AAIR":
            MODE = 7
        elif tempMode == "VOOR":
            MODE = 8
        elif tempMode == "VVIR":
            MODE = 9
        elif tempMode == "DOOR":
            MODE = 10
        else:
            MODE = 11

        #set integer value for activity threshold parameter
        if activity == "V-Low":
            ACTIVITY_THRESHOLD = 1
        elif activity == "Low":
            ACTIVITY_THRESHOLD = 2
        elif activity == "Low-Med":
            ACTIVITY_THRESHOLD = 3
        elif activity == "Med":
            ACTIVITY_THRESHOLD = 4
        elif activity == "Med-High":
            ACTIVITY_THRESHOLD = 5
        elif activity == "High":
            ACTIVITY_THRESHOLD = 6
        else:
            ACTIVITY_THRESHOLD = 7

        arrayToSend[14] = ACTIVITY_THRESHOLD
        
        ##########################################################################################################################################################
        ## HAVE TO FIX THIS
        finalArray = [0x8, 0x8]## pacing state + pacing mode + parameters

        finalArray += self.__intConversion__(MODE,                 1) ## pacing mode
        finalArray += self.__intConversion__(arrayToSend[0],       1) ## LRL
        finalArray += self.__intConversion__(arrayToSend[1],       1) ## URL
        finalArray += self.__intConversion__(arrayToSend[2],       1) ## max sensor rate
        finalArray += self.__intConversion__(arrayToSend[3],       2) ## fixed av delay
        finalArray += self.__intConversion__(arrayToSend[4],       2) ##  atr amp
        finalArray += self.__intConversion__(arrayToSend[5],       2) ## vtr amp
        finalArray += self.__intConversion__((arrayToSend[6]*10),  1) ## atr pulse w
        finalArray += self.__intConversion__((arrayToSend[7]*10),  1) ## vtr pulse w
        finalArray += self.__intConversion__((arrayToSend[8]*10),  1) ## atr sens
        finalArray += self.__intConversion__((arrayToSend[9]*10),  1) ## vtr sens
        finalArray += self.__intConversion__(arrayToSend[10],      2) ## vrp
        finalArray += self.__intConversion__(arrayToSend[11],      2) ## arp
        finalArray += self.__intConversion__(arrayToSend[12],      2) ## pvarp
        finalArray += self.__intConversion__(arrayToSend[13],      1) ## hyst
        finalArray += self.__intConversion__(arrayToSend[14],      1) ## rate smooth
        finalArray += self.__intConversion__(arrayToSend[15],      1) ## activity thresh
        finalArray += self.__intConversion__(arrayToSend[16],      1) ## react time
        finalArray += self.__intConversion__(arrayToSend[17],      1) ## response factor
        finalArray += self.__intConversion__(arrayToSend[18],      1) ## recovery time
     
        serialPacemaker.write(finalArray)
        print(*finalArray)
        print("Data sent")
        serialPacemaker.close()

        ##########################################################################################################################################################


    def __List__(self, *args):
        # global pacing mode to keep track of
        global dropList
        global currentDropList
        selectedPacingMode = dropOption.get()
        rowIndex = 5

        if(dropList):
            for i in range(len(dropList)):
                dropList[i].grid_remove()
            dropList = []
        if(currentDropList):
            for i in range(len(currentDropList)):
                currentDropList[i].grid_remove()
            currentDropList = []
        counter = 0

        for i in range(len(parameters)):  # set new parameters
            if(PacingModes[selectedPacingMode][i] == 1):
                dropList.append(tk.Label(self, text=parameters[i]))
                dropList[counter].grid(row=rowIndex, column=0)
                
                counter += 1

                dropList.append(tk.Entry(self, textvariable=tk.StringVar()))
                dropList[counter].grid(row=rowIndex, column=1)

                counter += 1

                dropList.append(tk.Label(self, text=parameterRanges[i]))
                dropList[counter].grid(row=rowIndex, column=2)

                counter +=1 
                rowIndex += 1

        ####################################
        ####### ADDED SECTION TO KEEP TRACK OF PARAMETER VALUES
        ####################################
        rowIndex += 1
        counter = 0

        currentDropList.append(tk.Label(self, text='Current Values', font=("Calibri", 15)))
        currentDropList[counter].grid(row=rowIndex, column=0, pady=20)
        
        counter += 1
        
        currentDropList.append(tk.Button(self, text="Send to Pacemaker", command=self.__serialCommunication__))
        currentDropList[counter].grid(row=rowIndex, column=1)
        
        counter += 1
        rowIndex += 1

        for i in range(len(parameters)):  # keep track of new parameters
            if(PacingModes[selectedPacingMode][i] == 1):

                currentDropList.append(tk.Label(self, text=parameters[i]))
                currentDropList[counter].grid(row=rowIndex, column=0)

                counter += 1

                currentDropList.append(tk.Label(self, text=str(userData[currentUser].parameters[selectedPacingMode][i])))
                currentDropList[counter].grid(row=rowIndex, column=1)

                counter += 1
                rowIndex += 1


    def __storeParamsData__(self, *args):
        file = open("parametersData.txt", "w")
        for i in userData:
            file.write(userData[i].getUserOutput()+"\n")
        file.close()


    def __updateParams__(self, *args):
        self.__getParams__()
        mode = dropOption.get()

        for i in userData:
            if(i == currentUser): 
                userData[currentUser].userOutput = i+","

                for mode in PacingModes:  
                    if(mode == 'AOO'):
                        userData[currentUser].userOutput += mode+","
                        counter = 0
                        
                        for k in PacingModes['AOO']:
                            if k == 1:
                                userData[currentUser].userOutput += userData[currentUser].parameters[mode][counter]+","
                            else:
                                userData[currentUser].userOutput += "0,"
                            counter += 1

                    elif(mode == 'AAI'):
                        userData[currentUser].userOutput += mode+","
                        counter = 0
                        
                        for k in PacingModes['AAI']:
                            if k == 1:
                                userData[currentUser].userOutput += userData[currentUser].parameters[mode][counter]+","
                            else:
                                userData[currentUser].userOutput += "0,"
                            counter += 1

                    elif(mode == 'VOO'):
                        userData[currentUser].userOutput += mode+","
                        counter = 0
                        
                        for k in PacingModes['VOO']:
                            if k == 1:
                                userData[currentUser].userOutput += userData[currentUser].parameters[mode][counter]+","
                            else:
                                userData[currentUser].userOutput += "0,"
                            counter += 1

                    elif(mode == 'VVI'):
                        userData[currentUser].userOutput += mode+","
                        counter = 0      

                        for k in PacingModes['VVI']:
                            if k == 1:
                                userData[currentUser].userOutput += userData[currentUser].parameters[mode][counter]+","
                            else:
                                userData[currentUser].userOutput += "0,"
                            counter += 1

                    elif(mode == 'DOO'):
                        userData[currentUser].userOutput += mode+","
                        counter = 0      

                        for k in PacingModes['DOO']:
                            if k == 1:
                                userData[currentUser].userOutput += userData[currentUser].parameters[mode][counter]+","
                            else:
                                userData[currentUser].userOutput += "0,"
                            counter += 1

                    elif(mode == 'AOOR'):
                        userData[currentUser].userOutput += mode+","
                        counter = 0      

                        for k in PacingModes['AOOR']:
                            if k == 1:
                                userData[currentUser].userOutput += userData[currentUser].parameters[mode][counter]+","
                            else:
                                userData[currentUser].userOutput += "0,"
                            counter += 1

                    elif(mode == 'AAIR'):
                        userData[currentUser].userOutput += mode+","
                        counter = 0      

                        for k in PacingModes['AAIR']:
                            if k == 1:
                                userData[currentUser].userOutput += userData[currentUser].parameters[mode][counter]+","
                            else:
                                userData[currentUser].userOutput += "0,"
                            counter += 1

                    elif(mode == 'VOOR'):
                        userData[currentUser].userOutput += mode+","
                        counter = 0      

                        for k in PacingModes['VOOR']:
                            if k == 1:
                                userData[currentUser].userOutput += userData[currentUser].parameters[mode][counter]+","
                            else:
                                userData[currentUser].userOutput += "0,"
                            counter += 1

                    elif(mode == 'VVIR'):
                        userData[currentUser].userOutput += mode+","
                        counter = 0      

                        for k in PacingModes['VVIR']:
                            if k == 1:
                                userData[currentUser].userOutput += userData[currentUser].parameters[mode][counter]+","
                            else:
                                userData[currentUser].userOutput += "0,"
                            counter += 1

                    elif(mode == 'DOOR'):
                        userData[currentUser].userOutput += mode+","
                        counter = 0      

                        for k in PacingModes['DOOR']:
                            if k == 1:
                                userData[currentUser].userOutput += userData[currentUser].parameters[mode][counter]+","
                            else:
                                userData[currentUser].userOutput += "0,"
                            counter += 1

        self.__storeParamsData__()
        messagebox.showwarning("Success", "Data has been updated!")
    
GUI().mainloop()
        