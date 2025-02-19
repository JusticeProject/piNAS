import subprocess
import time

###############################################################################

def getIPAddrs():
    result = subprocess.run("hostname -I", shell=True, capture_output=True)
    output = result.stdout.decode() + result.stderr.decode()
    addrs = output.split()
    return addrs

###############################################################################

def waitUntilNetworkReady():
    while (True):
        addrs = getIPAddrs()
        for addr in addrs:
            if (addr.count(".") == 3) and (addr != "127.0.0.1"):
                return
        time.sleep(0.5)

###############################################################################

print("Waiting for network...")
waitUntilNetworkReady()
print("...done waiting")
