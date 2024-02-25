from flask import Flask, render_template, request
import threading
import subprocess
import os
import time
from gpiozero import Button, LED
from main import sensor_main
# from Led_blink import Sensor

# Define the GPIO pin numbers for the button and LED
button_pin = 17
led_pin = 12
red = 24 # You can change this pin number based on your setup
blue = 10
green = 23

# Create LED objects for each pin
led_R = LED(red)
led_B = LED(blue)
led_G = LED(green)

# Create Button and LED objects
button = Button(button_pin)
led = LED(led_pin)
global ap_setup_done
# Initialize variables
pressed_time = None
led_on = False
ap_setup_done = False
main_flag = True
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
        
#         if ssid_list:
#             try:
#                 self.connection(str(ssid_list[0]))
#                 print(f"Successfully connected to {name}")
#             except Exception as exp:
#                 print(f"Couldn't connect to {name}. {exp}")
#                 overall_status = 1  # Update status if any connection fails


        for name in ssid_list:
            try:
                self.connection(name)
                print(f"Successfully connected to {name}")
            except Exception as exp:
                print(f"Couldn't connect to {name}. {exp}")
                overall_status = 1  # Update status if any connection fails

        return overall_status

    def connection(self, name):
        cmd = f"nmcli d wifi connect '{name}' password '{self.password}'"
        result = os.system(cmd)
       
        if result == 0:
            print(f"Successfully connected to {name}")
        else:
            print(f"Couldn't connect to {name}. Error code: {result}")
            raise Exception("Not Connected")

def run_ap_setup():
    led_R.off()
    script_path = os.path.join("/home/pi/Desktop/piconfig", "apsetup.sh")
    subprocess.run(["sudo", script_path])

# Update the path to the absolute path of your 'wifipass.txt' file
# file_path = '/home/pi/rpi-config-master/wifipass.txt'

def save_wifi_credentials(ssid, password):
    file_path = '/home/pi/rpi-config-master/wifipass.txt'
    print("Save_wifi_credential")
    # Save Wi-Fi credentials into wifipass.txt
    with open(file_path, 'w') as file:
        file.write(f"SSID={ssid}\nPassword={password}")
        print("file write succesfully")
#     if save_wifi_credentials(ssid.rstrip(),password.rstrip()):
#         print("save succesfully")
#         subprocess.run(["sudo", "reboot"])
#     else:
#         subprocess.run(["sudo", "reboot"])
#     delay(2000)
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
#         networkStatus(2)
        
def check_wifi_status():
    interface_name = "wlan0"  # Placeholder for the actual interface name
    file_path = '/home/pi/rpi-config-master/wifipass.txt'
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

            if len(lines) >= 2:
                ssid_line = lines[0].strip()
                password_line = lines[1]

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
#         networkStatus(2)
    # Return 1 if ID password is not configured
    # print("Wi-Fi credentials not found in the 'wifipass.txt' file.")
def ap_button():
    global main_flag
    led_R.on()
    led_G.on()
    led_B.on()
    pressed_time = None
    led_on = False
    print("Please press the button for 5 seconds")
    while True:
        if button.is_pressed and not led_on:
            pressed_time = time.time()
            led_on = True
            print("Button pressed, waiting for 5 seconds...")
        elif button.is_pressed and led_on:
            if time.time() - pressed_time >= 5:
                print("5 seconds elapsed, LED on")
                if not ap_setup_done:
                    main_flag = False
                    print("entering")
                    scan_wifi_networks()
                    save_network()
                    disconnect_and_enable_ap("wlan0")
#                     ap_setup_done=True
                    run_ap_setup()
                    led_R.on()
                    led.on()
                time.sleep(1)
                app.run(host='0.0.0.0', port=5000)
                return
        elif not button.is_pressed and led_on:
            led_on = False
            print("Button released, LED off")
            # return 1
def disable_auto_connect(interface_name):
    try:
        # List available connections and find the correct connection name
        list_result = subprocess.run(["nmcli", "-t", "-f", "NAME", "connection", "show"], capture_output=True, text=True)
        connection_names = list_result.stdout.strip().split('\n')
        
        # Find the connection name that corresponds to the given interface
        for connection_name in connection_names:
            connection_info = subprocess.run(["nmcli", "-g", "GENERAL.DEVICES", "connection", "show", connection_name], capture_output=True, text=True)
            if interface_name in connection_info.stdout.strip().split(':'):
                # Disable auto-connect for the identified connection
                subprocess.run(["sudo", "nmcli", "c", "modify", connection_name, "connection.autoconnect", "no"])
                print(f"Auto-connect disabled for {connection_name}")
                
                # Kill the wpa_supplicant process
                subprocess.run(["sudo", "pkill", "wpa_supplicant"])
                print("wpa_supplicant process killed")
                return

        # If no matching connection is found
        print(f"Error: No matching connection found for {interface_name}")
#         networkStatus(2)
    except Exception as e:
        print(f"Error disabling auto-connect: {e}")
#         networkStatus(2)
        
        
def disconnect_and_enable_ap(interface_name):
    try:
        # Disconnect from the current Wi-Fi network
        subprocess.run(["sudo", "iwconfig", interface_name, "essid", "off"])

        # Disable auto-connect for the Wi-Fi interface
        disable_auto_connect(interface_name)

        # Ensure that the wpa_supplicant process is killed after disabling auto-connect
        subprocess.run(["sudo", "pkill", "wpa_supplicant"])
        print("wpa_supplicant process killed")

        # Wait for a moment to ensure disconnection
        time.sleep(10)
        print("Disconnecting...")

        # Disable Wi-Fi interface
        subprocess.run(["sudo", "ifconfig", interface_name, "down"])
        time.sleep(2)

        # Enable Access Point (AP) mode
#         run_ap_setup()
        
        print(f"Disconnected from Wi-Fi on {interface_name} and switched to Access Point (AP) mode.")
    except Exception as e:
        print(f"Error: {e}")
#         networkStatus(2)

# def networkStatus(eventId):
# 	led_R.on()
# 	led_G.on()
# 	led_B.on()
# 	if(eventId==0):
# 		print("Network is connected. ON green led")
# 		led_G.off()
# 	elif(eventId==1):
# 		print("In AP mode. ON Blue led")
# 		led_R.off()
# 	else:
# 		print("Error occured. ON led red")

def scan_wifi_networks():
    try:
        result = subprocess.check_output(["sudo", "iwlist", "wlan0", "scan"])
        result = result.decode('utf-8')
        networks = [line.lstrip().split('ESSID:"')[1].split('"')[0] for line in result.split('\n') if "ESSID:" in line]
        
        return networks
    except subprocess.CalledProcessError:
        return []

networks = scan_wifi_networks()
def save_network():
    file_path = '/home/pi/rpi-config-master/wifi_networks.txt'
    with open(file_path, 'w') as file:
        for network in networks:
            file.write(network + '\n')

def main():
    global main_flag
    while main_flag:
#       Led_blink.blink_led(24)
        print("Geting sensor value")
        sensor_main()
        #path = '/home/pi/rpi-config-master/main.py'
        #cmd = ['sudo', 'python3', path]
        #subprocess.run(cmd)
#         Sensor()
        
# 		led_B.off()

if __name__ == '__main__':
    
        button_thread = threading.Thread(target=ap_button)
        button_thread.start()
        status = check_wifi_status()
        if status == 0:
            main_thread = threading.Thread(target=main)
            main_thread.daemon = True  # Set daemon to True to allow the main thread to exit even if this thread is still running
            main_thread.start()
#             ap_button()
            print("Connected to WiFi")
#             networkStatus(0)
        elif status == 1:
            print("ID password is not configured. Going into AP mode.")
            scan_wifi_networks()
            save_network()
            run_ap_setup()
            app.run(host='0.0.0.0', port=5000)
        elif status == 2:
            print("Disconnecting")
            scan_wifi_networks()
            save_network()           # Replace "wlan0" with the actual name of your Wi-Fi interface
            disconnect_and_enable_ap("wlan0")
#             run_ap_setup()
            app.run(host='0.0.0.0', port=5000)
                    
        else:
            print("Couldn't connect with existing ID pass, change it. Going into AP mode/n")
            print("Disconnecting")
            scan_wifi_networks()
            save_network() 
            disconnect_and_enable_ap("wlan0")
            run_ap_setup()
            app.run(host='0.0.0.0', port=5000)

