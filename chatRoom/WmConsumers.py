from channels.generic.websocket import WebsocketConsumer
from .views import MEETINGS
import json
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
            MEETINGS[mid]['participants'][id]['object'].send(json.dumps({"request_status":status}))
        elif(data['action']=="entry"):
            mid = str(data['mid'])
            id = data['id']
            if(id==MEETINGS[mid]['host']["key"].id):
                MEETINGS[mid]['host']["object"]=self
            else:
                MEETINGS[mid]['participants'][id]['object']=self
        elif(data['action']=="disconnect"):
            id = data['id']
            mid = str(data['mid'])
            MEETINGS[mid]['participants'][id]['key'].delete()
        else:
            id=data['id']
            mid=str(data['mid'])
            print(MEETINGS[mid]['participants'])
            try:
                name=MEETINGS[mid]['participants'][id]['key'].name
            except:
                name=MEETINGS[mid]['host']['key'].name
            msg=data['msg']
            for value in MEETINGS[mid]['participants']:
                item=MEETINGS[mid]['participants'][value]
                if(item==id):continue
                item['object'].send(json.dumps({"msg":msg,"name":name}))