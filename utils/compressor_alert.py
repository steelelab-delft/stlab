import smtplib
import os
import datetime
import os.path
import datetime
import glob
import sys
import time
from email.message import EmailMessage


# lrralxerojjirmpq   (app pass)

#LOGFOLDER = 'C:\\Entropy\\logs\\'
LOGFOLDER = 'D:\\logs\\'

def GetCurrentLogFolder():
    a = glob.glob(LOGFOLDER + '*-*-*/')
    #print(a)
    a = sorted(a)
    #print(a)
    ssa = a[-1]
    return ssa
        
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def GetCompStatus():
    ll = GetCurrentLogFolder()
    logfilename = glob.glob(ll + 'Status*')[0]

    with open(logfilename,'r') as f:
        lines = f.read().splitlines()
        last_line = lines[-2:]

    #print(last_line)

    stat = -99
    for ss in last_line:
        ss = ss.split(',')
        try:
            idx = ss.index('cpaerr')
        except ValueError:
            continue
        stat = int(float(ss[idx+1]))
        timestr = ' '.join(ss[:2])
        #timestr = '12-07-18 17:56:00'
        readdate = datetime.datetime.strptime(timestr, '%d-%m-%y %H:%M:%S')
        now = datetime.datetime.now()
        dt = time.mktime(now.timetuple()) - time.mktime(readdate.timetuple())
        #print(dt)
        if dt > 1800:
            raise RuntimeError('Too long since last compressor log!')

    if stat == -99:
        raise RuntimeError('No compressor data in logfile!')


    return stat

tmessage = 60
t0 = time.time()

while True:
    time.sleep(1)
    try:
        stat = GetCompStatus()
        if stat == 0:
            tt = time.time()
            if tt-t0 > tmessage:
                print("(Compressor monitor): It's",datetime.datetime.now(),"and all is well!")
                t0 = tt
            pass
        else:
            print('ALERT: COMPRESSOR ERROR! EMERGENCY! EMERGENCY!')
            gmail_user = 'steelelab.tudelft'
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(gmail_user, "SteeleLab_18")
            sent_from = 'Steelelab compressor alert service'  
            # to = ['m.d.jenkinssanchez@tudelft.nl']  
            to = ['steelelab-tnw@tudelft.nl']
            subject = 'EMERGENCY! COMPRESSOR ERROR!'  
            body = 'EMERGENCY! EMERGENCY! THERE IS AN EMERGENCY GOING ON!\n\nIT\'S STILL GOING ON!\n\nLooking forward to hearing from you,\n\nBest regards,\n\nSteelelab Compressor Alert Service'
            msg = EmailMessage()
            msg.set_content(body)
            msg['Subject'] = subject
            msg['From'] = sent_from
            msg['To'] = to
            server.send_message(msg)
            server.quit()
            break
    except RuntimeError as err:
        now = datetime.datetime.now()
        print(now.strftime('%d-%m-%y %H:%M:%S') + ': ',err)
        continue


