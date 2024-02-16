from flask import Flask, render_template, request
import subprocess
import os

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
        print(f"Successfully get ssids {ssid_list}")

        for name in ssid_list:
            try:
                self.connection(name)
            except Exception as exp:
                print(f"Couldn't connect to {name}. {exp}")
            else:
                print(f"Successfully connected to {name}")

def connection(self, name):
	cmd = f"nmcli d wifi connect {name} password {self.password}"
	if os.system(cmd) != 0:
		raise Exception("Not Connected")


def run_ap_setup():
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ap_setup.sh")
    subprocess.run(["sudo", script_path])

def save_wifi_credentials(ssid, password):    
    #save wifi credientials into wifipass.txt
    delay(5000)
    # Reboot the Raspberry Pi
    #subprocess.run(["sudo", "reboot"])

@app.route('/')
def hello():
    return render_template('config.html')

@app.route('/configure', methods=['POST'])
def configure():
    ssid = request.form.get('ssid')
    password = request.form.get('password')

    if ssid and password:
        print(ssid)
        print(password)
        # Save Wi-Fi credentials to wpa_supplicant.conf
        save_wifi_credentials(ssid, password)  
        return 'WiFi Configuration in progress...'
    else:
        return 'Invalid input. Both SSID and Password are required.'

int checkWifiStatus():
	SSID = ""
    password = ""
    interface_name = "wlan0"  # i.e., wlp2s0 
	return 1
	if(idpassExist):
		#fetch wifi credentials from wifipass.txt file
		finder = Finder(SSID, password, interface_name)
		int connectionStatus = finder.run()
		if(connectionStatus ==0):
			print("sucessfully coneected")
			return 0;
		elif(connectionStatus == 1):
			print("Error in connecting")
			return 2


if __name__ == '__main__': 
    bool status = checkWifiStatus();
    if(status == 0){
    print("Coneected to wifi")
    }
    elif(status==1){
    print("Id password is not configured, Going in AP mode")
    run_ap_setup()
    app.run(host='0.0.0.0', port=5000)
    }
    else{
    print("Could'nt connect with exisiting ID pass, change it. Going in AP mode")
    run_ap_setup()
    app.run(host='0.0.0.0', port=5000)
    }
   
    
