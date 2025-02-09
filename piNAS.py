from flask import Flask, redirect, send_from_directory, request, flash, get_flashed_messages
import os
import jinja2
import time
import subprocess

import Utilities

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # max size for uploads, 100MB

###############################################################################

env = jinja2.Environment(loader=jinja2.FileSystemLoader("./"))
driveListTemplate = env.get_template("template_drivelist.html")
fileListTemplate = env.get_template("template_fileList.html")
uploadErrorTemplate = env.get_template("template_uploadError.html")

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
    return redirect("/drivelist")

###############################################################################

@app.route("/<path:remotepath>", methods=["GET"])
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
        return send_from_directory(os.path.join(Utilities.MEDIA_PATH, folder), file) # as_attachment=True

###############################################################################

def allowedFile(filename):
    # Returns error string on error. Returns empty string for no error.
    if ("." not in filename):
        return "Missing ."

    if (".." in filename):
        return ".. not allowed"

    extension = filename.rsplit(".", 1)[1].lower()
    if (extension in ["mp3", "pdf"]):
        return "" # no error
    else:
        return "Only .mp3 and .pdf files allowed"

###############################################################################

@app.route("/<path:remotepath>", methods=["POST"])
def uploadFile(remotepath):
    if (".." in remotepath):
        return "", 404

    # TODO: add password protection for file uploads
    
    if ("file" not in request.files):
        flash("No file found")
        return redirect("/error")
    
    file = request.files["file"]
    # If the user does not select a file, the browser submits an empty file without a filename.
    if (file.filename == ""):
        flash("No selected file")
        return redirect("/error")

    errorMsg = allowedFile(file.filename)
    if (errorMsg == ""):
        # no problem detected so far, proceed
        fullLocalPath = os.path.join(Utilities.MEDIA_PATH, remotepath)
        fullLocalPath = os.path.join(fullLocalPath, file.filename)

        if (os.path.exists(fullLocalPath)):
            flash("File already exists")
            return redirect("/error")
        
        try:
            file.save(fullLocalPath)
        except:
            flash("Could not save file")
            return redirect("/error")
        return redirect(request.url)
    else:
        flash(errorMsg)
        return redirect("/error")

###############################################################################

@app.route("/error")
def uploadError():
    msgList = get_flashed_messages() # just a list of strings
    html = uploadErrorTemplate.render(msgList=msgList)
    return html

###############################################################################

@app.route("/eject/<drive>")
def ejectDrive(drive):
    if (".." in drive) or ("/" in drive):
        return "", 404
        
    Utilities.unmountDrive(drive)
    
    # redirect to main page
    return redirect("/drivelist")

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
    
