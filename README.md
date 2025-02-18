# piNAS
Lightweight network attached storage for Raspberry Pi. Files on a USB drive attached to the Pi are displayed through a web browser.

# Installation
## Set up the Firewall
```bash
sudo apt install ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw limit ssh/tcp
sudo ufw enable
sudo ufw allow 6512/tcp
sudo ufw logging off
sudo ufw status verbose
```
## Download the project files
```bash
sudo apt install git
git clone https://github.com/JusticeProject/piNAS.git
chmod +x ./piNAS/run.sh
```
## Install the needed Python packages in a virtual environment
```bash
sudo apt install python3-venv
python -m venv pythonenv --system-site-packages
source pythonenv/bin/activate
pip install flask
pip install waitress
deactivate
```
## Set it to run at boot
```bash
crontab -e
```
Then add this line at the bottom:
```bash
@reboot /home/pi/piNAS/run.sh &
```
Then C+X to save the file
### Reboot the Pi
```bash
sudo reboot now
```
### Open a web browser on a different computer and navigate to raspberrypi.local:6512/drivelist
