from flask import Flask, render_template, request
import subprocess
import os

app = Flask(__name__)

def run_ap_setup():
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ap_setup.sh")
    subprocess.run(["sudo", script_path])

def save_wifi_credentials(ssid, password):    
    # Create or open the wpa_supplicant.conf file using sudo
    wpa_conf_path = "/etc/wpa_supplicant/wpa_supplicant.conf"
    
    # Write the Wi-Fi credentials and additional details to the file
    with open(wpa_conf_path, 'a') as wpa_conf:
        wpa_conf.write("ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n")
        wpa_conf.write("update_config=1\n")
        wpa_conf.write(f'\nnetwork={{\n    ssid="{ssid}"\n    psk="{password}"\n    key_mgmt=WPA-PSK\n}}\n')

        #You can add more details if needed, such as:
        wpa_conf.write("country=IN\n")  # Set your country code
        wpa_conf.write("priority=1\n")   # Set priority for this network
        wpa_conf.write("scan_ssid=1\n")  # Enable SSID scanning (if needed)
    delay(5000)
    # Reboot the Raspberry Pi
    subprocess.run(["sudo", "reboot"])

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
def connect_to_wifi():
    try:
        # Restart the networking service to apply changes
        subprocess.run(["sudo", "systemctl", "restart", "networking"])

        print("Wi-Fi connection established successfully.")
    except Exception as e:
        print(f"Error connecting to Wi-Fi: {str(e)}")

if __name__ == '__main__':
    # Example usage
    connect_to_wifi()
    #run_ap_setup()
    #app.run(host='0.0.0.0', port=5000)
