# to automatically run this at boot, use the command: crontab -e
# then add this line at the bottom: @reboot /home/pi/piNAS/run.sh

cd /home/pi/piNAS
../pythonenv/bin/python piNAS.py &
