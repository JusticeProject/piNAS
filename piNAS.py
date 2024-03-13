import flask
import os
import jinja2
import time
import subprocess

import Utilities

app = flask.Flask(__name__)

###############################################################################

env = jinja2.Environment(loader=jinja2.FileSystemLoader("./"))
driveListTemplate = env.get_template("template_drivelist.html")
fileListTemplate = env.get_template("template_fileList.html")

###############################################################################

@app.route("/")
def index():
    return ""

###############################################################################

@app.route("/drivelist")
def drivelist():
    listOfDrives = Utilities.getListOfDrives()
    html = driveListTemplate.render(listOfDrives=listOfDrives)
    return html

###############################################################################

@app.route("/scanfordrives")
def scanForDrives():
    Utilities.scanForDrives()
    return flask.redirect("/drivelist")

###############################################################################

@app.route("/<path:remotepath>")
def handleLocalpath(remotepath):
    if (".." in remotepath):
        return "", 404

    fullLocalPath = os.path.join(Utilities.MEDIA_PATH, remotepath)
    if os.path.isdir(fullLocalPath):
        prevPage = ""
        if ("/" in remotepath):
            prevPage = remotepath.rsplit("/", maxsplit=1)[0]
        else:
            prevPage = "drivelist"

        dictOfFilesPaths = {}
        fileList = os.listdir(fullLocalPath)
        fileList.sort()
        for item in fileList:
            dictOfFilesPaths[item] = os.path.join(remotepath, item)
        html = fileListTemplate.render(folderName=remotepath, prevPage=prevPage,dictOfFilesPaths=dictOfFilesPaths)
        return html
    else:
        # if it's not in the format "folder/file" then we don't know how to handle it, the client may be asking for the website's icon
        if ("/" not in remotepath):
            return "", 404
        folder,file = remotepath.rsplit("/", maxsplit=1)
        # TODO: need to handle files with # in the name, currently the workaround is to remove it from the filename on the USB drive itself.
        # Another way is to modify the filename when creating the link: str.replace("#", "&#35;") 
        # then when the link is clicked and the filename is determined use str.replace("&#35;", "#") then send the file to the client
        return flask.send_from_directory(os.path.join(Utilities.MEDIA_PATH, folder), file) # as_attachment=True

###############################################################################

@app.route("/eject/<drive>")
def ejectDrive(drive):
    if (".." in drive) or ("/" in drive):
        return "", 404
        
    Utilities.unmountDrive(drive)
    
    # redirect to main page
    return flask.redirect("/drivelist")

###############################################################################

@app.route("/shutdown")
def shutdown():    
    # start shutting down after 3 seconds, run in background, 
    # this gives us time to respond to the client and the commands are not blocking us
    os.system("(sleep 3; sudo shutdown now) &")
    return "Shutting down..."

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

if __name__ == "__main__":
    waitUntilNetworkReady()
    app.run("0.0.0.0", 6512)
    
