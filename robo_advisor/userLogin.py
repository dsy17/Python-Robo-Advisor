from tkinter import *

from alpaca.common import APIError
from alpaca.trading import TradingClient

import userDatabase
import userInput


# changes UI view type from log-in to register and vice versa
def change_logreg(window, log_type):
    window.destroy()
    new_type = log_type
    if new_type == "Log-In":
        new_type = "Register"
    else:
        new_type = "Log-In"

    user_login(new_type)


# checks given username and password, if valid then user is logged in
def login_button(window):
    user = str(username.get())
    user_pass = str(password.get())
    if user != "" and user_pass != "":
        entry = userDatabase.login_connect(user, user_pass)
        if entry:
            window.destroy()
            userInput.log_in(user)
        else:
            error_label.config(text="Login failed", fg="#cf8488")
    else:
        error_label.config(text="Entries must not be empty", fg="#cf8488")


# registers new user with new username, password, and API keys to connect to Alpaca
def register_button():
    user = str(username.get())
    user_pass = str(password.get())
    get_api = str(api.get())
    get_secret = str(secret.get())
    try:
        tc = TradingClient(get_api, get_secret, paper=True)
        tc.get_account()
        if user != "" and user_pass != "":
            reg = userDatabase.register_connect(user, user_pass, get_api, get_secret)
            if reg:
                error_label.config(text="Register Successful", fg="#32a852")
            else:
                error_label.config(text="Username/API key already taken", fg="#cf8488")
        else:
            error_label.config(text="Entries must not be empty", fg="#cf8488")
    except APIError or ValueError:
        error_label.config(text="API connection could not be established", fg="#cf8488")


# main log-in UI
def user_login(log_type="Log-In"):
    login_type = log_type

    login = Tk()
    login.title("Robo-advisor App")
    login.resizable(False, False)

    welcome = Label(login, text="Welcome, User", font=('Helvetica bold', 25))
    header2 = Label(login, text=f"{login_type}:", font=('Helvetica bold', 15))

    user_label = Label(login, text="Enter username:")
    pass_label = Label(login, text="Enter password:")
    api_label = Label(login, text="Enter API key:")
    secret_label = Label(login, text="Enter Secret key:")

    enter_button = Button(login, text="Enter")
    global error_label
    error_label = Label(login)
    logreg_button = Button(login, command=lambda: change_logreg(login, login_type))

    global username
    global password
    global api
    global secret
    username = Entry(login)
    password = Entry(login, show='*')
    api = Entry(login)
    secret = Entry(login, show='*')

    if login_type == "Log-In":
        logreg_button["text"] = "Register"
        enter_button["command"] = lambda: login_button(login)
    else:
        logreg_button["text"] = "Log-In"
        enter_button["command"] = lambda: register_button()

    welcome.grid(row=0, column=0, padx=100, pady=(30, 0))
    header2.grid(row=1, pady=(20, 10))
    user_label.grid(row=2, pady=(20, 0))
    username.grid(row=3, pady=(15, 0))
    pass_label.grid(row=4, pady=(15, 0))
    password.grid(row=5, pady=(15, 0))
    if log_type != "Log-In":
        api_label.grid(row=6, pady=(15, 0))
        api.grid(row=7, pady=(15, 0))
        secret_label.grid(row=8, pady=(15, 0))
        secret.grid(row=9, pady=(15, 0))
    error_label.grid(row=10, pady=(5, 5))
    enter_button.grid(row=11, ipadx=20, pady=(10, 20))
    logreg_button.grid(row=12, padx=20, ipadx=25, pady=30, sticky="E")

    login.mainloop()


if __name__ == "__main__":
    user_login()
