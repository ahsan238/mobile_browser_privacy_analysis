import os
import sys
import json
import socket
import time
import os
import platform

ip = '192.58.122.65'
# ip = '152.14.92.31'
browser = sys.argv[1]
phone_id = sys.argv[2]


# am start -a android.intent.action.VIEW -d https://www.google.com/ - default browser command

# browser = "ddg"
# phone_id = "0C211JECB00876"
# phone_id = "12171JECB00327"


mitmport_map = {"chrome":50001,"brave":50002,"ddg":50003,"firefox":50004,'focus': 50005} # not relevant at the moment

port = 50006 # the port at which the server accepts all client conn
timeout = 10 # change this to 30

baseCommand = "shell am start -a android.intent.action.VIEW -d"
adbInitCommand = "adb -s {} ".format(phone_id)

blankPage = "about:blank"
screenshotDirPath = "./screenshots/"
# screenshotDirPath = sys.argv[3]
screenshotCmd = adbInitCommand + "exec-out screencap -p > {}".format(screenshotDirPath)

trancoFilename = "../tranco_87WV.csv"
tranco_list_url = "https://tranco-list.eu/download/87WV/full"

# websitesToLoadFileName = 'websites.txt'
# crawledWebsitesFileName = "crawled.txt"
# failedCrawledWebsiteFilename = "failedCrawl.txt"

crawledFile = 'crawled.json'
failedFile = 'failed.json'

crawledWebsites = {}
failedWebsites = {}


def getTrancoList():

    # from urllib.request import urlopen
    import csv
    import pandas as pd

    csv = pd.read_csv(trancoFilename)

    website_list = [row.values[1] for ind, row in csv.iterrows()]
    website_list = website_list[:10]

    return website_list
    
    


def chromeSequence(website):
    websiteLoadCommand = adbInitCommand+baseCommand+" {}".format(website)
    openChrome = adbInitCommand + "shell am start -n com.android.chrome/com.google.android.apps.chrome.Main"
    closeChrome = adbInitCommand + "shell pm clear com.android.chrome"
    untickBox = adbInitCommand + "shell input tap 78 1596"
    continueButton = adbInitCommand + "shell input tap 548 2221"
    crossButton = adbInitCommand + "shell input tap 135 2223"
    swipeBottom = adbInitCommand + "shell input touchscreen swipe 530 1420 530 250"
    openTabsCommand = adbInitCommand + "shell input tap 910 234"
    openTabsMenuCommand = adbInitCommand + "shell input tap 971 256"
    closeAllTabsCommand = adbInitCommand + "shell input tap 640 494"
    # closeTabCommand = adbInitCommand + "shell input tap 484 376"
    if os.system(openChrome) != 0:
        print("Failed openChrome")
        return
    time.sleep(1)

    if os.system(untickBox) != 0:
        print("Failed untickBox")
        return
    time.sleep(1)

    if os.system(continueButton) != 0:
        print("Failed continueButton")
        return
    time.sleep(1)

    if os.system(crossButton) != 0:
        print("Failed crossButton")
        return
    time.sleep(1)

    if os.system(websiteLoadCommand) != 0:
        print("Failed opening browser")
        return
    time.sleep(timeout/2)

    if os.system(screenshotCmd+website[7:]+".png") != 0:
        print("Failed opening browser")
        return
    time.sleep(timeout/2)

    if os.system(swipeBottom) != 0:
        print("Failed opening tab manager")
        return
    time.sleep(1)

    if os.system(screenshotCmd+website[7:]+"_2.png") != 0:
        print("Failed opening browser")
        return
    time.sleep(1)

    if os.system(closeChrome) != 0:
        print("Failed closeChrome")
        return
    time.sleep(1)




def braveSequence(website):
    websiteLoadCommand = adbInitCommand+baseCommand+" {}".format(website)
    openBrave = adbInitCommand + "shell am start -n com.brave.browser/com.google.android.apps.chrome.Main"
    closeBrave = adbInitCommand + "shell pm clear com.brave.browser"
    untickHelp = adbInitCommand + "shell input tap 75 2247"
    pressContinue = adbInitCommand + "shell input tap 525 1785"
    pressNotNow = adbInitCommand + "shell input tap 493 2063"
    pressCross = adbInitCommand + "shell input tap 998 744"
    openTabsCommand = adbInitCommand + "shell input tap 804 1487"
    openTabsMenuCommand = adbInitCommand + "shell input tap 981 2238"
    closeTabCommand = adbInitCommand + "shell input tap 494 331"
    swipeBottom = adbInitCommand + "shell input touchscreen swipe 530 1420 530 250"
    closeAllTabsCommand = adbInitCommand + "shell input tap 547 1876"

    if os.system(openBrave) != 0:
        print("Failed opening browser")
        return
    time.sleep(1)

    if os.system(untickHelp) != 0:
        print("Failed untickHelp")
        return
    time.sleep(0.7)

    if os.system(pressContinue) != 0:
        print("Failed pressContinue")
        return
    time.sleep(0.7)

    if os.system(pressNotNow) != 0:
        print("Failed pressNotNow")
        return
    time.sleep(0.7)

    if os.system(pressCross) != 0:
        print("Failed pressCross")
        return
    time.sleep(0.7)

    if os.system(websiteLoadCommand) != 0:
        print("Failed websiteLoadCommand")
        return
    time.sleep(timeout/2)

    if os.system(screenshotCmd+website[7:]+".png") != 0:
        print("Failed screenshotCmd")
        return
    time.sleep(timeout/2)

    if os.system(swipeBottom) != 0:
        print("Failed swipeBottom")
        return
    time.sleep(1)

    if os.system(screenshotCmd+website[7:]+"_2.png") != 0:
        print("Failed opening browser")
        return
    time.sleep(1)

    if os.system(closeBrave) != 0:
        print("Failed closeBrave")
        return
    time.sleep(1)




def firefoxSequence(website):
    websiteLoadCommand = adbInitCommand+baseCommand+" {}".format(website)
    openFirefox = adbInitCommand + "shell am start -n org.mozilla.firefox/.App"
    clearFirefox = adbInitCommand + "shell pm clear org.mozilla.firefox"
    openMenu = adbInitCommand + "shell input tap 1042 2225"
    openSettings = adbInitCommand + "shell input tap 658 2227"
    swipeBottom = adbInitCommand + "shell input touchscreen swipe 530 1420 530 250"
    aboutFirefox = adbInitCommand + "shell input tap 115 2269"
    touchFirefoxIcon = adbInitCommand + "shell input tap 229 493"
    goBack = adbInitCommand + "shell input tap 71 212"
    goToSecretSettings = adbInitCommand + "shell input tap 155 1945"
    toggleThirdPartyCA = adbInitCommand + "shell input tap 943 583"

    
    if os.system(openFirefox) != 0:
        print("Failed openFirefox")
        return
    time.sleep(0.7)

    if os.system(openMenu) != 0:
        print("Failed openMenu")
        return
    time.sleep(0.7)

    if os.system(openSettings) != 0:
        print("Failed openSettings")
        return
    time.sleep(0.7)

    if os.system(swipeBottom) != 0:
        print("Failed swipeBottom")
        return
    time.sleep(0.7)

    if os.system(aboutFirefox) != 0:
        print("Failed aboutFirefox")
        return
    time.sleep(0.7)

    for i in range(6):
        if os.system(touchFirefoxIcon) != 0:
            print("Failed touchFirefoxIcon")
            return
        time.sleep(0.3)

    if os.system(goBack) != 0:
        print("Failed goBack")
        return
    time.sleep(0.7)

    if os.system(swipeBottom) != 0:
        print("Failed swipeBottom")
        return
    time.sleep(0.7)

    if os.system(goToSecretSettings) != 0:
        print("Failed goToSecretSettings")
        return
    time.sleep(0.7)

    if os.system(toggleThirdPartyCA) != 0:
        print("Failed toggleThirdPartyCA")
        return
    time.sleep(0.7)

    if os.system(goBack) != 0:
        print("Failed goBack")
        return
    time.sleep(0.5)

    if os.system(goBack) != 0:
        print("Failed goBack")
        return
    time.sleep(0.7)

    if os.system(websiteLoadCommand) != 0:
        print("Failed websiteLoadCommand")
        return
    time.sleep(timeout/2)

    if os.system(screenshotCmd+website[7:]+".png") != 0:
        print("Failed screenshotCmd")
        return
    time.sleep(timeout/2)

    if os.system(swipeBottom) != 0:
        print("Failed swipeBottom")
        return
    time.sleep(0.7)

    if os.system(screenshotCmd+website[7:]+"_2.png") != 0:
        print("Failed screenshotCmd")
        return
    time.sleep(1)

    if os.system(clearFirefox) != 0:
        print("Failed clearFirefox")
        return
    time.sleep(2)

    



def focusSequence(website):
    websiteLoadCommand = adbInitCommand+baseCommand+" {}".format(website)
    openFocus = adbInitCommand +"shell am start -n org.mozilla.focus/org.mozilla.focus.activity.MainActivity"
    clearFocus = adbInitCommand + "shell pm clear org.mozilla.focus"
    swipeBottom = adbInitCommand + "shell input touchscreen swipe 530 1420 530 250"
    pressSkip = adbInitCommand + "shell input tap 75 208" 
    typeConfigText = adbInitCommand + "shell input text about:config" 
    pressEnter = adbInitCommand + "shell input keyevent 66" 
    tapConfigSearchBar = adbInitCommand + "shell input tap 605 373" 
    typeConfigOption = adbInitCommand + "shell input text enterprise" 
    toggleOption = adbInitCommand + "shell input tap 817 548" 
    closeTabCommand = adbInitCommand + "shell input tap 591 2195"
    # closeTabCommand = adbInitCommand + "shell input tap 489 1081"

    if os.system(openFocus) != 0:
        print("Failed openFocus")
        return
    time.sleep(1)

    if os.system(pressSkip) != 0:
        print("Failed pressSkip")
        return
    time.sleep(1)

    if os.system(typeConfigText) != 0:
        print("Failed typeConfigText")
        return
    time.sleep(1)

    if os.system(pressEnter) != 0:
        print("Failed pressEnter")
        return
    time.sleep(1)

    if os.system(tapConfigSearchBar) != 0:
        print("Failed tapConfigSearchBar")
        return
    time.sleep(1)

    if os.system(typeConfigOption) != 0:
        print("Failed typeConfigOption")
        return
    time.sleep(1)

    for i in range(2):
      if os.system(toggleOption) != 0:
        print("Failed tapConfigSearchBar")
        return
      time.sleep(0.7)
      
    if os.system(closeTabCommand) != 0:
        print("Failed closeTabCommand")
        return
    time.sleep(1)

    if os.system(websiteLoadCommand) != 0:
        print("Failed opening browser")
        return
    time.sleep(timeout/2)

    if os.system(screenshotCmd+website[7:]+".png") != 0:
        print("Failed opening browser")
        return
    time.sleep(timeout/2)

    if os.system(swipeBottom) != 0:
        print("Failed closing tab")
        return
    time.sleep(1)

    if os.system(screenshotCmd+website[7:]+".png") != 0:
        print("Failed opening browser")
        return
    time.sleep(1)

    if os.system(clearFocus) != 0:
        print("Failed clearFocus")
        return
    time.sleep(1)




def ddgSequence(website):
  websiteLoadCommand = adbInitCommand+baseCommand+" {}".format(website)
  closeDdg = adbInitCommand + "shell pm clear com.duckduckgo.mobile.android"
  openDdg = adbInitCommand + "shell am start -n com.duckduckgo.mobile.android/com.duckduckgo.app.launch.Launcher"
  pressIamNew  = adbInitCommand + "shell input tap 477 1160"
  swipeBottom = adbInitCommand + "shell input touchscreen swipe 530 1420 530 250"
  openTabsCommand = adbInitCommand + "shell input tap 931 240"
  openTabsMenuCommand = adbInitCommand + "shell input tap 1028 214"
  closeTabCommand = adbInitCommand + "shell input tap 476 408"
  closeAllTabsCommand = adbInitCommand + "shell input tap 664 366"
  reloadCommand = adbInitCommand + " shell input keyevent 82"

  if os.system(openDdg) != 0:
      print("Failed opening browser")
      return
  time.sleep(1)

  if os.system(pressIamNew) != 0:
      print("Failed pressIamNew")
      return
  time.sleep(1)

  if os.system(websiteLoadCommand) != 0:
      print("Failed opening browser")
      return
  time.sleep(timeout/2)

  if os.system(screenshotCmd+website[7:]+".png") != 0:
      print("Failed opening browser")
      return
  time.sleep(1)

  if os.system(swipeBottom) != 0:
      print("Failed opening tab manager")
      return
  time.sleep(timeout/2)

  if os.system(screenshotCmd+website[7:]+".png") != 0:
      print("Failed opening browser")
      return
  time.sleep(1)

  if os.system(closeDdg) != 0:
      print("Failed closeDdg")
      return
  time.sleep(1)




def readFile(filename):
  with open(filename) as fp:
    d = [x.replace('\n','') for x in fp.readlines()]
  fp.close()
  print(d)
  return d


def updateWebsiteToList(file_name, website):
  with open(file_name,'a') as fp:
    fp.write(website+"\n")
    fp.close()


def establishConnection(ip,port):
  s = socket.socket()
  print('establishing',ip,port)
  s.connect((ip,port))
  print('connection established')
  return s

def updateLogWithWebsite(logfile, logDict, website,val):
  if website not in logDict:
    logDict[website] = val
  else:
    logDict[website] += val

  with open(logfile) as fp:
    temp = json.load(fp)
    fp.close()

  if website not in temp:
    temp[website] = val
  else:
    temp[website]+= val

  with open(logfile,'w') as fp:
    json.dump(temp,fp,indent=4)
    fp.close()

def initDir():
  if not os.path.isdir("./screenshots"):
    os.mkdir("./screenshots")
  


def initLogFiles():
  # initiate the failed and crawled list.
  t1 = {} # crwaled
  t2 = {} # failed
  
  if os.path.isfile("crawled.json"):
    with open("crawled.json") as fp:
      t1 = json.load(fp)
      fp.close()
  else:
    with open("crawled.json",'w') as fp:
      json.dump({},fp,indent=4)
      fp.close()

  if os.path.isfile("failed.json"):
    with open("failed.json") as fp:
      t2 = json.load(fp)
      fp.close()
  else:
    with open("failed.json",'w') as fp:
      json.dump({},fp,indent=4)
      fp.close()
  
  return t1, t2

def resetLogFiles():
  with open("crawled.json",'w') as fp:
    json.dump({},fp,indent=4)
    fp.close()

  with open("failed.json",'w') as fp:
    json.dump({},fp,indent=4)
    fp.close()


def cleanBrowser():
    if browser == 'firefox':
        clearFirefox = adbInitCommand + "shell pm clear org.mozilla.firefox"
        if os.system(clearFirefox) != 0:
            print("Failed clearFirefox")
            return
        time.sleep(2)

    elif browser == "focus":
        clearFocus = adbInitCommand + "shell pm clear org.mozilla.focus"
        if os.system(clearFocus) != 0:
          print("Failed clearFocus")
          return
        time.sleep(2)

    elif browser == "brave":
        clearBrave = adbInitCommand + "shell pm clear com.brave.browser"
        if os.system(clearBrave) != 0:
          print("Failed clearBrave")
          return
        time.sleep(2)

    elif browser == "chrome":
        clearChrome = adbInitCommand + "shell pm clear com.android.chrome"
        if os.system(clearChrome) != 0:
          print("Failed clearChrome")
          return
        time.sleep(2)

    elif browser == "ddg":
        clearDdg = adbInitCommand + "shell pm clear com.duckduckgo.mobile.android"
        if os.system(clearDdg) != 0:
          print("Failed clearDdg")
          return
        time.sleep(2)


        

    





def main():
  resetLogFiles()
  cleanBrowser()
  crawledWebsites, failedWebsites = initLogFiles()
  initDir()
  websites = getTrancoList()
  crawled = list(crawledWebsites.keys())
  # crawled = []
  s = establishConnection(ip,port)
  print(browser)
  s.send(browser.encode()) # step 1: send the browser name

  s.recv(1024).decode()

  for w in websites:
    
    if w in crawled: # check if the website has already been crawled
      print("already crawled {}".format(w))
      continue

    print("sending {}".format(w))

    s.send(w.encode()) # step 2: send the website name

    sig = s.recv(1024).decode() # step 2.1: if signal == "1", this means server has mitmproxy server up and running. the client can start loading the website.

    # load the website on the mobile
    websitename = "https://"+w
    if browser == "chrome":
      chromeSequence(websitename)
    elif browser == "brave":
      braveSequence(websitename)
    elif browser == "ddg":
      ddgSequence(websitename)
    elif browser == "firefox":
      firefoxSequence(websitename)
    elif browser == "focus":
      focusSequence(websitename)

    s.send("0".encode()) # step 3: send success code
    
    fileExistsSig = s.recv(1024).decode() # step 3.1: make sure the dump file exists at the server end

    if fileExistsSig == "0":
      print('website loaded successfully')
      updateLogWithWebsite("crawled.json",crawledWebsites,w,1)
    elif fileExistsSig == "-1":
      print('first launch failed')
      relaunchStatus = s.recv(1024).decode() # step 3.2: signal from server to confirm if they are ready for another launch
      if relaunchStatus == "1": # the server has set up another mitm instance. launch the website again
        if browser == "chrome":
          chromeSequence(websitename)
        elif browser == "brave":
          braveSequence(websitename)
        elif browser == "ddg":
          ddgSequence(websitename)
        elif browser == "firefox":
          firefoxSequence(websitename)
        elif browser == "focus":
          focusSequence(websitename)
      s.send("0".encode()) # step 3.3: send success code so that server can close the mitmproxy instance

      sig = s.recv(1024).decode() # step 3.4: ask server if the website was loaded successfully. if not then keep it in the log

      if sig == "0":
        print('second launch successful')
        updateLogWithWebsite("crawled.json",crawledWebsites,w,1)
      elif sig =="-1":
        print('second launch failed')
        updateLogWithWebsite("crawled.json",crawledWebsites,w,-1)
        updateLogWithWebsite("failed.json",failedWebsites,w,1)





  s.send("-1".encode()) # step 4: ask server to close instance after all websites loaded

  s.close() # close the client

main()


# getTrancoList(tranco_list_url)