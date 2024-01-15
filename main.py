import network_interface_module as nim
import user_auth as auth

network_info = nim.NetworkDevices()
user = auth.UserConfig()

while not user.logged:
    user.login()

user_request = ""
while user_request != "exit":
    user_request = input("> ")
    match user_request:
        case "show interfaces":
            network_info.show_interfaces()
        case "exit":
            break
