import platform    # For getting the operating system name
import subprocess  # For executing a shell command
import time
import argparse
from tkinter import *

from datetime import datetime
from datetime import timedelta
import sys
VERSION = "081221:1018"
#---------------------------------------------------------------------------------------------------------------------
class outage:
        startTime =0
        endTime=0
        delta =0
#---------------------------------------------------------------------------------------------------------------------
def pingx(host,file, curtime):
    param = '-n' if platform.system().lower()=='windows' else '-c'
    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]
    myOut=""
    try:
        subprocess.check_output(command)
    except subprocess.CalledProcessError as e:
        #file.write(curtime)
        #file.write("\n")
        #file.write(e.output.decode())
        #file.flush()
        return False
    return True
#-----------------------------------------------------------------------------------------------------
def buttonCallback():
    return True
#-----------------------------------------------------------------------------------------------------
def formatDump(x):
    if x.delta > issueThreshold:
        stat = (x.startTime.strftime("%D, %H:%M:%S") + "  ->  " + x.endTime.strftime("%D, %H:%M:%S") + " [duration:" +
                str(x.deltaAsString).split(".", 1)[0] + "] << MAJOR >>\n")
    else:
        stat = (x.startTime.strftime("%D, %H:%M:%S") + "  ->  " + x.endTime.strftime("%D, %H:%M:%S") + " [duration:" +
                str(x.deltaAsString).split(".", 1)[0] + "]\n")
    return(stat)

#------------------------------------------------------------------------------------------------------------------
def dumpOutages():
    if Console:
        print ("\n\n--------list of outages since ",str(initialTime).split(".",1)[0]," ---------------------------------")
        print ("   START TIME                END TIME")
        for x in listOfOutages:
            print(formatDump(x),end='')
        #if x.delta> issueThreshold:
        #    print (x.startTime.strftime("%D, %H:%M:%S"), "  ->  ", x.endTime.strftime("%D, %H:%M:%S")," [duration:",str(x.deltaAsString).split(".",1)[0],"] << MAJOR >>")
        #else:
        #    print(x.startTime.strftime("%D, %H:%M:%S"), "  ->  ", x.endTime.strftime("%D, %H:%M:%S"), " [duration:",
        #          str(x.deltaAsString).split(".",1)[0], "]")
        print ("--------------------------------------------------------------")
# ------------------------------------------------------------------------------------------------------------------
def dumpOutagesTk():
    tk2 =Tk()
    S = Scrollbar(tk2)
    T = Text(tk2, height=15, width=90)
    S.pack(side=RIGHT, fill=Y)
    T.pack(side=LEFT, fill=Y)
    S.config(command=T.yview)
    T.config(yscrollcommand=S.set)
    stat=("--------list of outages since "+ str(initialTime).split(".", 1)[0]+ " ---------------------------------\n")
    T.insert(END, stat)
    stat= ("   START TIME             END TIME\n")
    T.insert(END, stat)
    for x in listOfOutages:
        T.insert(END, formatDump(x))
    tk2.update_idletasks()
    tk2.update()
#------------------------------------------------------------------------------------------------------- main


# ------------------------------------------------- Instantiate the parser
parser = argparse.ArgumentParser(description='Pings a site at a specified interval.\n Reports success count and details on individual failures')
parser.add_argument('destination', type=str,  help=' the site that will be pinged  (e.g. google.com)')
parser.add_argument('interval', type=int,  help='time between pings in seconds')
parser.add_argument('-file', type=int,  help='log file  ( default is pinger.txt ')
parser.add_argument('-issueThreshold', type=int,  help='Outages larger than this number of seconds will be flagged as a major issue ')
parser.add_argument('-tk', dest='useTk', default=False, action='store_true')
parser.add_argument('-noConsole', dest='noConsole', default=False, action='store_true')
args = parser.parse_args()
service =  args.destination
interval = HealthyPingInterval= args.interval   #how long to sleep between pings
if args.file is not None:
        logfile = args.file
else:
        logfile = 'pinger.txt'

if args.issueThreshold is not None:
        issueThreshold = args.issueThreshold
else:
        issueThreshold = 15
if args.useTk:
        useTk= True
else:
        useTk= False
if args.noConsole:
    Console = False
else:
    Console = True
# ---------------------------------------------------- set up some defaults
pingCount =0        # count of ping attempts
minorIssue=0
majorIssue=0
problemPingInterval =3
listOfOutages =[]
numOfFailures =0
noResponse = False

file = open(logfile, 'w')
now = datetime.now()
#------------- splash
startedAt = now.strftime("%D, %H:%M:%S")
splash = "*** Pinger "+VERSION+" Started at " + startedAt +" on "  + platform.system()+\
         "\n->Pinging " + service + " every " + str(interval) +\
         " seconds.\n->Log file is 'pinger.txt'\n->Outage Pings will happen every " +\
         str(problemPingInterval) +\
        " seconds.\n->Outages lasting more than "+str(issueThreshold) + " seconds will be flagged as major outage\n"
if Console: print(splash)
file.write(splash)
initialTime = datetime.now()
if useTk: #-----------------------------------set up up
    tk =Tk()
    tk.geometry("300x50")
    tk.configure(background='white')
    tk.title('Status:OK')
    tkStatus=""
    tkStatus2=""
    var = StringVar()
    var2 = StringVar()
    lbl = Label(tk, text=tkStatus, fg='black',bg='white',font=("Helvetica", 10),textvariable=var)
    lbl.place(x=1, y=1)
    lbl2 = Label(tk, text=tkStatus2, fg='black',bg='white', font=("Helvetica", 10),textvariable=var2)
    lbl2.place(x=1, y=30)
    but= Button(tk, text="i", command=dumpOutagesTk)
    but.pack(side=BOTTOM)
    but.pack(side=RIGHT)
    menubar = Menu(tk)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Dump log", command=dumpOutagesTk)
    filemenu.add_command(label="About", command=dumpOutagesTk)
    filemenu.add_command(label="Exit", command=dumpOutagesTk)
    menubar.add_cascade(label="File", menu=filemenu)
    tk.config(menu=menubar)
#-------------------Main Loop
while True:
    now = datetime.now()
    startedAt = now.strftime("%D, %H:%M:%S")
    pingStatus = pingx(service, file, startedAt)    #----- Check net status
    pingCount +=1
    if pingStatus == True :
        interval = HealthyPingInterval
        if noResponse:  # are currently in an outage but the ping is now responding so we are recovered.  log it and append it to the list
            outageCapture.endTime = datetime.now()
            diff = outageCapture.endTime - outageCapture.startTime
            outageCapture.delta = diff.total_seconds()
            outageCapture.deltaAsString = str(timedelta(seconds = outageCapture.delta))
            listOfOutages.append(outageCapture)
            if outageCapture.delta > issueThreshold:
                majorIssue +=1
            else:
                minorIssue +=1
            dumpOutages()
            file.write(formatDump(listOfOutages[-1]))
            file.flush()
            noResponse=False   # back to normal
            if useTk:
                tk.title('Status:OK')
                tk.configure(background='white')
                lbl.configure(bg='white')
                lbl2.configure(bg='white')
                tk.update_idletasks()
                tk.update()
        for t in range(interval, 0,-1 ):    # wait some time before sending next ping
            uptime = now - initialTime   # calc how long its been since started
            strUptime =str(uptime)
            hhmmss= strUptime.split(".",1)
            if Console: print("\r", startedAt, "[T+",hhmmss[0],"] >>", t, "<< Responses =", pingCount, ", Failures:", numOfFailures,"(major:", majorIssue,", minor:",minorIssue,")       ", end=' ', flush=True)
            tkStatus= startedAt+ "[T+"+hhmmss[0]+"] >>"+ str(t)+ "<<"
            tkStatus2=  "Responses ="+ str(pingCount)+ "  Failures:"+ str(numOfFailures)+" (major:"+ str(majorIssue)+ " , minor:"+str(minorIssue)+")"
            if useTk:
                var.set(tkStatus)
                var2.set(tkStatus2)
                tk.update_idletasks()
                tk.update()
            time.sleep(1)

        if Console:print("\r", startedAt, "[T+", hhmmss[0], "] >>PING<< Responses =", pingCount, ", Failures:",
            numOfFailures, "(major:", majorIssue, ", minor:", minorIssue, ")           ", end=' ', flush=True)
        if useTk:
            tkStatus = startedAt + "[T+" + hhmmss[0] + "] >>PING<<"
            tkStatus2 = "Responses =" + str(pingCount) + "  Failures:" + str(numOfFailures) + " (major:" + str(
                majorIssue) + " , minor:" + str(minorIssue) + ")"
            var.set(tkStatus)
            var2.set(tkStatus2)
            tk.update_idletasks()
            tk.update()
            time.sleep(.25)
    else :
        # capture details of outage
        if noResponse == False: # first time through
            if Console:print("\n", startedAt, " ******** NO RESPONSE TO PING********  \n", end=' ', flush=True)
            interval = problemPingInterval  # when connection is down, ping  fast
            retryCount=0;

            outageCapture = outage()
            outageCapture.startTime = datetime.now()
            noResponse = True
            numOfFailures +=1
        else:
            retryCount +=1

        if useTk:
            tk.title('Status:NO RESPONSE')
            tk.configure(background='red')
            lbl.configure(bg='red')
            lbl2.configure(bg='red')
            var.set( startedAt+ " NO RESPONSE TO PING"  )
            var2.set(" Waiting for recovery. Retry:"+str(retryCount))
            tk.update_idletasks()
            tk.update()

        if Console:print("\r", startedAt, " ******** Waiting for network recovery  (", retryCount, ") ********  ", end=' ', flush = True)
        time.sleep(interval)
    sys.stdout.flush()

