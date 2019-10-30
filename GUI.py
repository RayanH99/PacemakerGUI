import tkinter as tk
from tkinter import messagebox
import os

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
        ## Currently only storing 8 of the 18 parameters! Assignment 2 will expand on these params
        parameters = ['Lower Rate Limit', 'Upper Rate Limit', 'Atrial Amplitude', 'Ventricular Amplitude', 'Atrial Pulse Width', 
                      'Ventricular Pusle Width', 'VRP', 'ARP']

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
            #file = open("parametersData.txt", "r")

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
        self.parameters['AOO'] = ['0']*8
        self.parameters['VOO'] = ['0']*8
        self.parameters['AAI'] = ['0']*8
        self.parameters['VVI'] = ['0']*8

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
            'AOO': [1, 1, 1, 0, 1, 0, 0, 0],
            'VOO': [1, 1, 0, 1, 0, 1, 0, 0],
            'AAI': [1, 1, 1, 0, 1, 0, 0, 1],
            'VVI': [1, 1, 0, 1, 0, 1, 1, 0]
        }

        global dropOption
        dropOption = tk.StringVar()

        global dropList
        dropList = []

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

    def __List__(self, *args):
        global dropList

        mode = dropOption.get()
        rowIndex = 5

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

    def __getParams__(self, *args):
        global validParameters
        validParameters = {
            'Lower Rate Limit': [str(x) for x in range(30, 55, 5)]+[str(x) for x in range(50, 91, 1)]+[str(x) for x in range(90, 180, 5)],
            'Upper Rate Limit': [str(x) for x in range(50, 180, 5)],
            'Atrial Amplitude': ['O']+[str(x*0.1) for x in range(5, 36, 1)]+[str(x*0.1) for x in range(35, 75, 5)],
            'Ventricular Amplitude': ['O']+[str(x*0.1) for x in range(5, 33, 1)]+[str(x*0.1) for x in range(35, 75, 5)],
            'Atrial Pulse Width': ['0.05']+[str(x*0.1) for x in range(1, 20, 1)],
            'Ventricular Pusle Width': ['0.05']+[str(x*0.1) for x in range(1, 20, 1)],
            'VRP': [str(x) for x in range(150, 500, 10)],
            'ARP': [str(x) for x in range(150, 500, 10)]
        }

        mode = dropOption.get()
        
        for i in range(1, len(dropList), 2):
            if(dropList[i].get() in validParameters[dropList[i-1]['text']]):
                userData[currentUser].parameters[mode][parameters.index(dropList[i-1]['text'])] = dropList[i].get()
            else:
                messagebox.showwarning("Error!", "Invalid parameter values!")
                break

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

                    elif(mode == 'VOO'):
                        userData[currentUser].userOutput += mode+","
                        counter = 0
                        
                        for k in PacingModes['VOO']:
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

                    elif(mode == 'VVI'):
                        userData[currentUser].userOutput += mode+","
                        counter = 0      

                        for k in PacingModes['VVI']:
                            if k == 1:
                                userData[currentUser].userOutput += userData[currentUser].parameters[mode][counter]+","
                            else:
                                userData[currentUser].userOutput += "0,"
                            counter += 1
        
        self.__storeParamsData__()
    
GUI().mainloop()
        