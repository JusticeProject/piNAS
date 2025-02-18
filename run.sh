# to automatically run this at boot, use the command: crontab -e
# then add this line at the bottom: @reboot /home/pi/piNAS/run.sh &

cd /home/pi/piNAS
source ../pythonenv/bin/activate
python waitUntilNetworkReady.py
waitress-serve --port=6512 'piNAS:app' &
