import os
import re
import subprocess

###############################################################################

MEDIA_PATH = "/media/" + os.getlogin() + "/"
REGEX_DRIVE = re.compile(r"sd[a-z][1-9]*") # the number can be matched 0 or more times

###############################################################################

def isUSBDevice(dev):
    command = "udevadm info --query=all --name=" + dev + "| grep ID_BUS"
    result = subprocess.run(command, shell=True, capture_output=True)
    output = result.stdout.decode() + result.stderr.decode()
    if ("usb" in output):
        return True
    else:
        return False

###############################################################################

def getUSBStorageDevPaths():
    allDevs = os.listdir("/dev")
    storageDevs = []
    
    for dev in allDevs:
        if (REGEX_DRIVE.match(dev)): # check if it is sda, sdb1, etc.
            if (isUSBDevice(dev)):
                storageDevs.append(dev)
    
    # if sdb1 is available then mark sdb for removal from list
    toIgnore = []
    for dev in storageDevs:
        if (len(dev) > 3):
            toIgnore.append(dev[:3])
            
    # get rid of repeats in toIgnore
    toIgnore = list(set(toIgnore))
    
    # finally, remove the ones we don't need
    for item in toIgnore:
        storageDevs.remove(item)
    
    # add /dev/ to the beginning to make it a path
    storageDevPaths = []
    for dev in storageDevs:
        storageDevPaths.append("/dev/" + dev)
    
    storageDevPaths.sort()
    return storageDevPaths

###############################################################################

def getMountFolder(allMounts, devPath):
    for mountline in allMounts:
        if (devPath in mountline):
            try:
                location = mountline.split(" ")[2]
                return location
            except:
                pass
                
    return ""

###############################################################################

def getAllMounts():
    result = subprocess.run("mount", shell=True, capture_output=True)
    output = result.stdout.decode() + result.stderr.decode()
    return output.split("\n")

###############################################################################

def isFolderMounted(allMounts, fullFolderPath):
    for mountline in allMounts:
        if (fullFolderPath in mountline):
            mountedFolder = mountline.split(" ", maxsplit=2)[2]
            mountedFolder = mountedFolder.split(" type ", maxsplit=1)[0]
            if (mountedFolder == fullFolderPath):
                return True
            
    return False

###############################################################################

def getUserFriendlyName(fullDevPath):
    dev = fullDevPath.rsplit("/", maxsplit=1)[1]

    command = "udevadm info --query=all --name=" + dev
    result = subprocess.run(command, shell=True, capture_output=True)
    output = result.stdout.decode() + result.stderr.decode()
    
    ID_VENDOR="Unknown"
    ID_MODEL="Unknown"
    
    for line in output.split("\n"):
        if ("ID_VENDOR=" in line):
            ID_VENDOR = line.split("=")[1]
        if ("ID_MODEL=" in line):
            ID_MODEL = line.split("=")[1]

	# example: SanDisk_Cruzer_sda1
    return ID_VENDOR + "_" + ID_MODEL + "_" + dev

###############################################################################

def mountDev(fullDevPath):
    # get user friendly name for the device instead of sdb1
    friendlyName = getUserFriendlyName(fullDevPath)
    fullMediaPath = os.path.join(MEDIA_PATH, friendlyName)
    
    if (os.path.exists(fullMediaPath) == False):
        # create the folder and the necessary parent folders
        result = os.system("sudo mkdir --parents " + fullMediaPath)
        if (result != 0):
            # could not create media folder, don't continue
            return
    
    os.system("sudo mount " + fullDevPath + " " + fullMediaPath)

###############################################################################

def getListOfDrives():
    listofdrives = []
    allMounts = getAllMounts()
    
    # only return them if they are mounted
    if (os.path.exists(MEDIA_PATH)):
        folders = os.listdir(MEDIA_PATH)
        for folder in folders:
            if (isFolderMounted(allMounts, os.path.join(MEDIA_PATH, folder))):
                listofdrives.append(folder)
        
    return listofdrives

###############################################################################

def scanForDrives():
    allMounts = getAllMounts()
    storageDevPaths = getUSBStorageDevPaths()
    
    for devPath in storageDevPaths:
        folder = getMountFolder(allMounts, devPath)
		# if it's not mounted then mount it
        if (len(folder) == 0):
            mountDev(devPath)
    
    return

###############################################################################

def unmountDrive(folderName):
    localpath = os.path.join(MEDIA_PATH, folderName)
    result = os.system("sudo umount '" + localpath + "'")
    
    if (result == 0):
        os.system("sudo rmdir '" + localpath + "'")

