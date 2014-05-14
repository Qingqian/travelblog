from django.db import models
# from geoposition.fields import GeopositionField

# Create your models here.
from django.contrib.auth.models import User

class Post(models.Model):
	text = models.CharField(max_length=200)
	time = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User)
	pic = models.ImageField(upload_to="images", blank=True)
	location = models.CharField(max_length=50, blank=True)
	latitude = models.FloatField(blank=True, default=0)
	longitude = models.FloatField(blank=True, default=0)
	def __unicode__(self):
		return self.text

class Friend(models.Model):
	user1 = models.ForeignKey(User, related_name='friend_user1')
	user2 = models.ForeignKey(User, related_name='friend_user2')

class FriendRequest(models.Model):
	src = models.ForeignKey(User, related_name='friendrequest_src')
	dst = models.ForeignKey(User, related_name='friendrequest_dst')

class Visit(models.Model):
	src = models.ForeignKey(User, related_name='follow_src')
	dst = models.ForeignKey(User, related_name='follow_dst')
	time = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
	text = models.CharField(max_length=200)
	src_user = models.ForeignKey(User, related_name='comment_src_user')
	post = models.ForeignKey(Post)
	time = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
	text = models.CharField(max_length=200)
	src = models.ForeignKey(User, related_name='message_src')
	dst = models.ForeignKey(User, related_name='message_dst')
	time = models.DateTimeField(auto_now_add=True)
