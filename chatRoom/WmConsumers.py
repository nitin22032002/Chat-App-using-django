from channels.generic.websocket import WebsocketConsumer
from .views import MEETINGS
import json
from .models import Message
from datetime import datetime
class waitingRoomRequest(WebsocketConsumer):
    def connect(self):
        self.accept()
    def receive(self, text_data=None, bytes_data=None):
        data=json.loads(text_data)
        if(data.get("action",False)):
            id=data['id']
            mid = str(data['mid'])
            MEETINGS[mid]['participants'][id]['key'].delete()
        mid=str(data['mid'])
        id=data['id']
        MEETINGS[mid]['participants'][id]['object']=self
class chatRoomRequest(WebsocketConsumer):
    def connect(self):
        self.accept()
    def receive(self, text_data=None, bytes_data=None):
        data=json.loads(text_data)
        if(data['action']=="accept_request"):
            mid = str(data['mid'])
            id = data['id']
            status=data['status']
            MEETINGS[mid]['participants'][id]['object'].send(json.dumps({"action":"request","request_status":status}))
        elif(data['action']=="remove"):
            mid = str(data['mid'])
            id = data['id']
            pid=data['host_id']
            if(pid==MEETINGS[mid]['host']['key'].id):
                MEETINGS[mid]['participants'][id]['object'].send(json.dumps({"action":'leave'}))
        elif(data['action']=="block"):
            mid = str(data['mid'])
            id = data['id']
            pid = data['host_id']
            if (pid == MEETINGS[mid]['host']['key'].id):
                MEETINGS[mid]['participants'][id]['key'].block_status=True
                MEETINGS[mid]['participants'][id]['key'].save()
                MEETINGS[mid]['participants'][id]['object'].send(json.dumps({"action":"block"}))
        elif (data['action'] == "unblock"):
            mid = str(data['mid'])
            id = data['id']
            pid = data['host_id']
            if (pid == MEETINGS[mid]['host']['key'].id):
                MEETINGS[mid]['participants'][id]['key'].block_status=False
                MEETINGS[mid]['participants'][id]['key'].save()
                MEETINGS[mid]['participants'][id]['object'].send(json.dumps({"action": "unblock"}))
        elif(data['action']=="entry"):
            mid = str(data['mid'])
            id = data['id']
            if(id==MEETINGS[mid]['host']["key"].id):
                MEETINGS[mid]['host']["object"]=self
            MEETINGS[mid]['participants'][id]['object']=self
            name=MEETINGS[mid]['participants'][id]['key'].name
            MEETINGS[mid]['participants'][id]['key'].block_status=False
            MEETINGS[mid]['participants'][id]['key'].save()
            for item in MEETINGS[mid]['participants'].values():
                uname=item['key'].name
                uid=item['key'].id
                obj=item['object']
                self.send(json.dumps({"action":"add_user","name":uname,"id":uid}))
                if(self!=obj):
                    obj.send(json.dumps({"action":"add_user","name":name,"id":id}))
            messages=Message.objects.filter(room_id=mid).all()
            for item in messages:
                sender_id = item.sender_id
                name = MEETINGS[mid]['participants'][sender_id]['key'].name
                date = item.date
                msg = item.message
                self.send(json.dumps({"action":"message","msg":msg,"name":name,"date":str(date),"id":sender_id}))
        else:
            id=data['id']
            mid=str(data['mid'])
            name=MEETINGS[mid]['participants'][id]['key'].name
            status=MEETINGS[mid]['participants'][id]['key'].block_status
            date=datetime.now()
            msg=data['msg']
            if(not status):
                msgObj=Message()
                msgObj.room_id=mid
                msgObj.message=msg
                msgObj.sender_id=id
                msgObj.date=date
                msgObj.save()
                for item in MEETINGS[mid]['participants'].values():
                    if(not item['key'].block_status):
                        item['object'].send(json.dumps({"action":"message","msg":msg,"name":name,"date":str(date),"id":id}))
            else:
                MEETINGS[mid]['host']['object'].send(json.dumps({"action":"message","msg":msg,"name":name,"date":str(date),"id":id}))
                MEETINGS[mid]['participants'][id]['object'].send(json.dumps({"action":"message","msg":"You Are Blocked By Host","name":"Group Chat","date":str(date),"id":""}))