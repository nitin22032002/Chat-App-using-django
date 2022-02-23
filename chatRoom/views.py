from django.shortcuts import render,redirect
import  random
import jwt
import qrcode
import json
from DiscusionForum.views import sendOtp
from django.http import JsonResponse
from .models import Users,Room,Person,Message
from DiscusionForum.settings import BASE_DIR
from datetime import datetime
datetime.now().replace()
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
        end_time=Room.objects.get(id=mid).date_end
        current=datetime.now().replace(second=0,microsecond=0)
        diff=(end_time.date()-current.date()).total_seconds()
        diff+=abs((end_time.time().hour-current.time().hour)*60*60)
        diff+=abs((end_time.time().minute-current.time().minute)*60)
        id=request.session['meetinguser']['id']
        name=request.session['meetinguser']['name']
        host_id=MEETINGS[mid]["host"]['key'].id
        return render(request,"chatRoom.html",{"mid":mid,"id":id,"host_id":host_id,"name":name,"diff":diff})
    except Exception as e:
        print(e)
        return redirect("/joinmeeting")

def updateMeeting(request,id=None):
    try:
        obj=Room.objects.get(id=id)
        if(obj):
            obj.date_start=str(obj.date_start)[:-9]
            obj.date_end=str(obj.date_end)[:-9]
            return render(request,"updateMeeting.html",{"data":obj})
        return redirect("/meetinglist")
    except:
        return redirect("/")

def updateMeetingContent(request):
    try:
        data=request.POST
        id=data['meetingid']
        topic=data['name']
        start=data['start']
        end=data['end']
        room=Room.objects.get(id=id)
        if(room):
            room.date_end=end
            room.name=topic
            room.date_start=start
            room.save()
        return redirect("/meetinglist")
    except Exception as e:
        print(e)
        return redirect("/meetinglist")

def joinPerson(request):
    try:
        data=request.POST
        id=data['id']
        name=data['name']
        tk=data['tk']
        session=request.session
        meeting=getMeeting(id)
        current = datetime.now().replace(second=0, microsecond=0)
        msg=""
        if (len(meeting)>0 and session.get("user", False) and ((meeting[3].date()<current.date()) or (meeting[3].date()==current.date() and meeting[3].time()<=current.time())) and ((meeting[4].date()>current.date()) or (meeting[4].date()==current.date() and meeting[4].time()>current.time()))):
            if(session['user']['data']['id']==meeting[0]):
                addper=addPersonInMeeting(session['user']['data']['name'])
                MEETINGS[id]={"host":{'key':addper,"object":None},"participants":{}}
                MEETINGS[id]["participants"][addper.id] = {"key": addper, "object": None}
                request.session['meetinguser']={"status":"host","name":addper.name,"id":addper.id,"mid":id}
                return redirect(f"/waitingroom/?id={id}")
        else:
            pass

        if(len(meeting)==0):
            msg="Invalid Meeting Details"
        elif((meeting[4].date()<current.date()) or (meeting[4].date()==current.date() and meeting[4].time()<=current.time())):
            msg="Meeting Expire"
        elif(((meeting[3].date()>current.date()) or (meeting[3].date()==current.date() and meeting[3].time()>current.time()))):
            msg="Meeting not start yet"
        elif(not MEETINGS.get(id,None)):
            msg="Host Not Start Meeting Yet"
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
                        MEETINGS[id]['host']['object'].send(json.dumps({"action":"entry","data":{"name":name,"id":addper.id}}))
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
            MEETINGS[id]['host']['object'].send(json.dumps({"action":"entry","data": {"name": name, "id": addper.id}}))
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
def leave(request):
    global MEETINGS
    try:
        if (request.session.get("meetinguser", False)):
            data = request.session['meetinguser']
            id = data['id']
            mid = data['mid']
            status = data['status']
            if(request.session.get("visit",False)):
                del request.session['visit']

            if (status == "host"):
                for item in MEETINGS[mid]["participants"].values():
                    if (item['key'].id == id): continue
                    item['object'].send(json.dumps({"action": "host_left"}))
                obj = MEETINGS[mid]['participants'][id]['key']
                obj.delete()
                messages=Message.objects.filter(room_id=mid).all()
                for item in messages:
                    item.delete()
                del MEETINGS[mid]["host"]
            else:
                for item in MEETINGS[mid]["participants"].values():
                    if (item['key'].id == id): continue
                    item['object'].send(json.dumps({"action": "user_left","name":MEETINGS[mid]["participants"][id]['key'].name,"id":id}))
                obj = MEETINGS[mid]['participants'][id]['key']
                obj.delete()
            del MEETINGS[mid]['participants'][id]
            del request.session['meetinguser']
            return redirect("/joinmeeting")
        else:
            return redirect("/joinmeeting")
    except Exception as e:
        print(e)
        return redirect("/joinmeeting")
def cancel(request):
    global MEETINGS
    try:
        if(request.session.get("meetinguser",False)):
            data=request.session['meetinguser']
            id=data['id']
            mid=data['mid']
            del request.session['visit']
            MEETINGS[mid]["host"]["object"].send(json.dumps({"action":"cancel_request","id":id}))
            obj=MEETINGS[mid]['participants'][id]['key']
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
        if(request.session.get("meetinguser",False) and not request.session.get("visit",False)):
            data=request.session['meetinguser']
            request.session['visit']=True
            name=data['name']
            status=data['status']
            id=data['id']
            mid=data['mid']
            meeting=getMeeting(mid)
            if(len(meeting)>0):
                mname=meeting[5]
                return render(request,"waitingRoom.html",{"status":status,"name":name,"mname":mname,"id":id,"mid":mid})
            else:
                return redirect("/joinmeeting")

        else:
            cancel(request)
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