from django.shortcuts import render,redirect
import  random
import jwt
import qrcode
import json
from DiscusionForum.views import sendOtp
from django.http import JsonResponse
from .models import Users,Room,Person
from DiscusionForum.settings import BASE_DIR
from datetime import datetime
secretkey="itissecretesrtig"
MEETINGS={}
def uniqueid():
    seed = random.getrandbits(32)
    while True:
       yield seed
       seed += 1
uniqueid_seq=uniqueid()
def addPersonInMeeting(name):
    per=Person()
    per.name=name
    per.save()
    return per
def getMeeting(id):
    meeting = Room.objects.filter(id=id)
    if (len(meeting)>0):
        meeting=meeting[0]
        host_id = meeting.host_id
        password = meeting.meeting_password
        status = meeting.meeting_password_status
        start = meeting.date_start
        end = meeting.date_end
        name = meeting.name
        return host_id,password,status,start,end,name
    else:
        return []
def validate(request):
    try:
        data = request.POST
        id = data['id']
        name = data['name']
        meeting = getMeeting(id)
        if (meeting[1] == data['password']):
            addper = addPersonInMeeting(name)
            MEETINGS[id]["participants"][addper.id]={"key": addper, "object": None}
            request.session['meetinguser'] = {"status": "user", "name": addper.name, "id": addper.id,
                                              "mid": id}
            MEETINGS[id]['host']['object'].send(json.dumps({"entry": {"name": name, "id": addper.id}}))
            return redirect(f"/waitingroom/?id={id}")
        else:
            return render(request,"passwordCheck.html",{"name":name,"meetingid":id,"msg":"Password Not match"})
    except Exception as e:
        print(e)
        return redirect("/joinmeeting")
def meetingArea(request):
    try:
        mid=request.GET['id']
        id=request.session['meetinguser']['id']
        return render(request,"chatRoom.html",{"mid":mid,"id":id})
    except Exception as e:
        print(e)
        return redirect("/joinmeeting")
def joinPerson(request):
    try:
        data=request.POST
        id=data['id']
        name=data['name']
        tk=data['tk']
        session=request.session
        meeting=getMeeting(id)
        msg=""
        if (len(meeting)>0 and session.get("user", False)):
            if(session['user']['data']['id']==meeting[0]):
                addper=addPersonInMeeting(session['user']['data']['name'])
                MEETINGS[id]={"host":{'key':addper,"object":None},"participants":{}}
                request.session['meetinguser']={"status":"host","name":addper.name,"id":addper.id,"mid":id}
                return redirect(f"/meetingarea/?id={id}")
        else:
            pass
        if(len(meeting)==0):
            msg="Invalid Meeting Details"
        elif(meeting[4]<datetime.now().astimezone()):
            msg="Meeting Expire"
        elif(meeting[3]>datetime.now().astimezone() or id not in MEETINGS ):
            msg="Meeting not start yet"
        if(msg!=""):
            return render(request,"joinMeeting.html",{"meetingid":id,"name":name,"tk":tk,"msg":msg})
        if(meeting[2]):
            if(tk!=""):
                try:
                    data=jwt.PyJWT().decode(tk,secretkey,["HS256"])
                    if(meeting[1]==data['password']):
                        addper = addPersonInMeeting(name)
                        MEETINGS[id]["participants"][addper.id]={"key": addper, "object": None}
                        request.session['meetinguser'] = {"status": "user", "name": addper.name, "id": addper.id,
                                                          "mid": id}
                        MEETINGS[id]['host']['object'].send(json.dumps({"entry":{"name":name,"id":addper.id}}))
                        return redirect(f"/waitingroom/?id={id}")
                    else:
                        return redirect("/joinmeeting")
                except Exception as e:
                    print(e)
                    return redirect("/joinmeeting")
            else:
                return render(request,"passwordCheck.html",{"name":name,"meetingid":id})
        else:
            addper = addPersonInMeeting(name)
            MEETINGS[id]["participants"][addper.id]={"key": addper, "object": None}
            request.session['meetinguser'] = {"status": "user", "name": addper.name, "id": addper.id, "mid": id}
            MEETINGS[id]['host']['object'].send(json.dumps({"entry": {"name": name, "id": addper.id}}))
            return redirect(f"/waitingroom/?id={id}")
    except Exception as e:
        print(e)
        return redirect("/")
def landingPage(request):
    if(request.session.get('user',False)):
        print(request.session.get('user',False))
        return render(request,"userHome.html")
    return render(request,"home.html")
def createMeeting(request):
    if (request.session.get('user', False)):
        return render(request,"createMeeting.html")
    return redirect("/")
def saveMeeting(request):
    try:
        id=next(uniqueid_seq)
        host_id=request.session['user']["data"]['id']
        data=request.POST
        topic=data['name']
        start=data['start']
        end=data['end']
        status=data.get('passwordstatus',False)
        room=Room()
        if(status):
            status=True
            password="".join(random.sample(["0","1","2","3","4","5","6","7","8","9"],5))
            room.meeting_password=password
        room.id = id
        room.meeting_password_status=status
        room.host_id=host_id
        room.date_end=end
        room.name=topic
        room.date_start=start
        room.save()
        return redirect("/roomdetails/?id=%d"%(id))
    except Exception as e:
        print(e)
        return redirect("/createmeeting")
def deleteMeeting(request):
    try:
        room = Room.objects.get(id=request.GET['id'])
        room.delete()
        return redirect("/meetinglist")
    except Exception as e:
        print(e)
        return redirect("/")
def getRoomDeatils(request):
    try:
        room=Room.objects.get(id=request.GET['id'])
        data={"id":room.id}
        if(room.meeting_password_status):
            data['password']=room.meeting_password
        token=jwt.PyJWT().encode(payload=data,key=secretkey)
        qr=qrcode.make(data)
        qr.save(f"{BASE_DIR}/publicfiles/images/qrroom.png")
        return render(request,"showRoomDetails.html",{"room":room,"token":token})
    except Exception as e:
        print(e)
        return redirect("/")
def allMetings(request):
    try:
        if(request.session.get("user",False)):
            meetings=Room.objects.filter(host_id=request.session['user']['data']['id']).all()
            return render(request,"showAllMeetings.html",{"meetings":meetings})
        return redirect("/")
    except Exception as e:
        print(e)
        return redirect("/")
def logout(request):
    try:
        del request.session['user']
        del request.session['otp']
        return redirect("/")
    except Exception as e:
        print(e)
        return redirect("/")
def signIn(request):
    return render(request,"auth.html")
def joinMeeting(request):
    try:
        name=""
        meetingid=""
        if(request.session.get("user",False)):
            name=request.session['user']['data']['username']
        if(request.GET.get('tk',False)):
            try:
                data=jwt.PyJWT().decode(request.GET['tk'],secretkey,["HS256"])
                meetingid=data['id']
            except Exception as e:
                print(e)
        return render(request,"joinMeeting.html",{"meetingid":meetingid,"name":name,"tk":request.GET.get("tk","")})
    except Exception as e:
        print(e)
        return  redirect("/")
def cancel(request):
    try:
        if(request.session.get("meetinguser",False)):
            data=request.session['meetinguser']
            id=data['id']
            mid=data['mid']
            obj=Person.objects.get(id=id)
            obj.delete()
            del MEETINGS[mid]['participants'][id]
            del request.session['meetinguser']
            return redirect("/joinmeeting")
        else:
            return redirect("/joinmeeting")
    except Exception as e:
        print(e)
        return redirect("/joinmeeting")
def waitingRoom(request):
    try:
        if(request.session.get("meetinguser",False)):
            data=request.session['meetinguser']
            name=data['name']
            id=data['id']
            mid=data['mid']
            meeting=getMeeting(mid)
            if(len(meeting)>0):
                mname=meeting[5]
                return render(request,"waitingRoom.html",{"name":name,"mname":mname,"id":id,"mid":mid})
            else:
                return redirect("/joinmeeting")

        else:
            return redirect("/joinmeeting")
    except Exception as e:
        print(e)
        return redirect("/joinmeeting")
def login(request):
    emailid=request.POST['emailid']
    password=request.POST['password']
    data=Users.objects.filter(emailid=emailid,password=password)
    if(len(data)==0):
        return render(request,"auth.html",{"msg":"Invalid Authentication"})
    else:
        data=data[0]
        data={"name":data.name,"username":data.username,"emailid":data.emailid,"id":data.id}
        # print(data)
        request.session['user']={"data":data}
        return redirect("/")
def addUser(request):
    request.session['user']=request.POST
    if(len(Users.objects.filter(emailid=request.POST['emailid']))>0):
        return redirect("/signin")
    return sendOtps(request)
def verifyUser(request):
    if(request.GET["otp"]==request.session["otp"]):
        data=request.session['user']
        obj=Users.objects.create(name=data['name'],username=data['username'],emailid=data['emailid'],password=data['password'])
        obj.save()
        request.session['user']={"data":{"name":obj.name,"id":obj.id,"username":obj.username,"emailid":obj.emailid}}
        del request.session['otp']
        return JsonResponse({"status":True})
    else:
        return JsonResponse({"status":False})
def sendOtps(request):
    status = sendOtp(request.session["user"]['emailid'])
    if (status[0]):
        request.session['otp'] = str(status[1])
        return redirect("/verifyuser")
    return JsonResponse({"status": False})
def otp(request):
    return render(request,"otp.html")