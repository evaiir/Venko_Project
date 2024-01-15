import getpass

class UserConfig:
    def __init__(self):
        self.logged = False
        self.user = "admin"
        self.password = "passwd"

    def login(self):
        if not self.logged:
            user_inpt = input("Login: ")
            password_inpt = getpass.getpass("Password: ")

            if user_inpt == self.user and password_inpt == self.password:
                print(f"WELCOME TO THE PROGRAM!")
                self.logged = True
            else:
                print(f"Failed to login! Try again:\n")
