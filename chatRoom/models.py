from django.db import models



class Message(models.Model):
    room_id = models.IntegerField()
    sender_id = models.IntegerField()
    message = models.CharField(max_length=1000000000)
    date = models.DateTimeField()


class Person(models.Model):
    name = models.CharField(max_length=1000)
    block_status = models.BooleanField(default=True)


class Room(models.Model): 
    host_id = models.IntegerField()
    name = models.CharField(max_length=100,default="group meeting 1")
    meeting_password = models.CharField(max_length=8,default="xxxxx")
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    meeting_password_status = models.BooleanField(default=False)

class Users(models.Model):
    name=models.CharField(max_length=1000)
    emailid=models.CharField(max_length=100)
    username=models.CharField(max_length=1000)
    password=models.CharField(max_length=25)
