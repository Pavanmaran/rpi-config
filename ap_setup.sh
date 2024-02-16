#!/bin/bash

# Install hostapd and dnsmasq
sudo apt-get update
sudo apt-get install -y hostapd dnsmasq

# Stop services if they are running
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

# Configure static IP for wlan0
echo "interface wlan0" | sudo tee -a /etc/dhcpcd.conf
echo "static ip_address=192.168.4.1/24" | sudo tee -a /etc/dhcpcd.conf
sudo systemctl restart dhcpcd

# Configure hostapd
echo "interface=wlan0" | sudo tee -a /etc/hostapd/hostapd.conf
echo "ssid=RasBhari" | sudo tee -a /etc/hostapd/hostapd.conf
echo "hw_mode=g" | sudo tee -a /etc/hostapd/hostapd.conf
echo "channel=7" | sudo tee -a /etc/hostapd/hostapd.conf
echo "wmm_enabled=0" | sudo tee -a /etc/hostapd/hostapd.conf
echo "macaddr_acl=0" | sudo tee -a /etc/hostapd/hostapd.conf
echo "auth_algs=1" | sudo tee -a /etc/hostapd/hostapd.conf
echo "ignore_broadcast_ssid=0" | sudo tee -a /etc/hostapd/hostapd.conf

# Start services
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd

# Configure dnsmasq
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
echo "interface=wlan0" | sudo tee -a /etc/dnsmasq.conf
echo "dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h" | sudo tee -a /etc/dnsmasq.conf

# Restart services
sudo systemctl enable dnsmasq
sudo systemctl start dnsmasq

# Enable IP forwarding
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"
echo "up iptables-restore < /etc/iptables.ipv4.nat" | sudo tee -a /etc/network/interfaces
