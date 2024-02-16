from flask import Flask, render_template, request
import subprocess
import os
import time

app = Flask(__name__)


class Finder:
    def __init__(self, server_name, password, interface_name):
        self.server_name = server_name
        self.password = password
        self.interface_name = interface_name

    def run(self):
        command = f"sudo iwlist {self.interface_name} scan | grep -ioE 'ssid:\"(.*{self.server_name}.*)'"
        result = os.popen(command).readlines()

        ssid_list = [item.lstrip('SSID:').strip('"\n') for item in result]
        print(f"Successfully got SSIDs: {ssid_list}")

        # Initialize status to success
        overall_status = 0

        for name in ssid_list:
            try:
                self.connection(name)
                print(f"Successfully connected to {name}")
            except Exception as exp:
                print(f"Couldn't connect to {name}. {exp}")
                overall_status = 1  # Update status if any connection fails

        return overall_status

    def connection(self, name):
        cmd = f"nmcli d wifi connect {name} password {self.password}"
        if os.system(cmd) != 0:
            raise Exception("Not Connected")

def run_ap_setup():
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ap_setup.sh")
    subprocess.run(["sudo", script_path])

# Update the path to the absolute path of your 'wifipass.txt' file
file_path = '/home/pi/piconfig/wifipass.txt'

def save_wifi_credentials(ssid, password):
    # Save Wi-Fi credentials into wifipass.txt
    with open(file_path, 'w') as file:
        file.write(f"SSID={ssid}\nPassword={password}")
    #delay(2000)
    # Reboot the system after writing the file
    subprocess.run(["sudo", "reboot"])


@app.route('/')
def hello():
    return render_template('config.html')

@app.route('/configure', methods=['POST'])
def configure():
    ssid = request.form.get('ssid')
    password = request.form.get('password')

    if ssid and password:
        print(f"SSID: {ssid}")
        print(f"Password: {password}")
        # Save Wi-Fi credentials to wifipass.txt
        save_wifi_credentials(ssid, password)
        return 'WiFi Configuration in progress...'
    else:
        return 'Invalid input. Both SSID and Password are required.'
def check_wifi_status():
    interface_name = "wlan0"  # Placeholder for the actual interface name
    file_path = '/home/pi/piconfig/wifipass.txt'
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

            if len(lines) >= 2:
                ssid_line = lines[0].strip()
                password_line = lines[1].strip()

                if ssid_line.startswith("SSID=") and password_line.startswith("Password="):
                    SSID = ssid_line.split("=")[1]
                    password = password_line.split("=")[1]

                    # Placeholder for your logic to check WiFi status
                    # Return 0 if successfully connected, 2 if an error occurred
                    print("WiFi Credentials:")
                    print(f"SSID: {SSID}")
                    print(f"Password: {password}")
                    
                    finder = Finder(SSID, password, interface_name)
                    connectionStatus = finder.run()
                    if connectionStatus == 0:
                        print("Successfully connected")
                        return 0
                    elif connectionStatus == 1:
                        print("Error in connecting")
                        return 2
                    else: print("something not well")
                else:
                    print("Invalid format in the 'wifipass.txt' file.")
                    return 1
            else:
                print("Insufficient lines in the 'wifipass.txt' file.")
                return 1

    except Exception as e:
        print(f"Error reading Wi-Fi credentials: {e}")

    # Return 1 if ID password is not configured
    # print("Wi-Fi credentials not found in the 'wifipass.txt' file.")
    # return 1



if __name__ == '__main__':
    status = check_wifi_status()
    if status == 0:
        print("Connected to WiFi")
    elif status == 1:
        print("ID password is not configured. Going into AP mode.")
        run_ap_setup()
        app.run(host='0.0.0.0', port=5000)
    else:
        print("Couldn't connect with existing ID pass, change it. Going into AP mode")
        run_ap_setup()
        app.run(host='0.0.0.0', port=5000)
