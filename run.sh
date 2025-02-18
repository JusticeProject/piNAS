# to automatically run this at boot, use the command: crontab -e
# then add this line at the bottom: @reboot /home/pi/piNAS/run.sh &

cd /home/pi/piNAS
../pythonenv/bin/python waitUntilNetworkReady.py
../pythonenv/bin/waitress-serve --port=6512 'piNAS:app' &
