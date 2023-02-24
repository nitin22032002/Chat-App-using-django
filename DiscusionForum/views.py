import smtplib
from . import Codes 
from random import randint
def sendOtp(emailid):
    try:
        # smtp=smtplib.SMTP("smtp.gmail.com",587)
        # smtp.starttls()
        # smtp.login(Codes.code['emailid'],Codes.code['password'])
        otp=randint(1000,9999)
        message="Your Otp Is %d"%(otp)
        # smtp.sendmail(Codes.code['emailid'],emailid,message)
        # smtp.quit()
        # smtp.close()
        print(message,end="\n\n")
        return True,otp
    except Exception as e:
        print(e)
        return [False]
