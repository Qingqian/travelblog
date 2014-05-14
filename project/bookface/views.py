from django.shortcuts import render, redirect, get_object_or_404
from bookface.models import *
from bookface.forms import *

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

from django.core.mail import EmailMessage

from django.http import HttpResponse, Http404
from mimetypes import guess_type

import random

from django.db.models import Q
from itertools import chain

import cgi


# Create your views here.
@login_required
def home(request):
	context = {}
	notice_list = []
	if 'addfriend' in request.GET:
		dst_username = request.GET['addfriend']
		dst = User.objects.get(username=dst_username)
		new_request = FriendRequest(src=request.user, dst=dst)
		new_request.save()
		notice_list.append('Friend Request is sent!')
	if 'requestsrc' in request.GET:
		request_src = request.GET['requestsrc']
		reply = request.GET['reply']
		src_user = User.objects.get(username=request_src)
		if int(reply) == 1:
			new_friend = Friend(user1=request.user, user2=src_user)
			new_friend.save()
			notice_list.append('Friend added!')
		else:
			notice_list.append('Friend request declined.')
		FriendRequest.objects.filter(src=src_user, dst=request.user).delete()
			
	request_list = FriendRequest.objects.filter(dst=request.user)

	friend_list_1 = Friend.objects.filter(user1=request.user).values_list('user2', flat=True)
	friend_list_2 = Friend.objects.filter(user2=request.user).values_list('user1', flat=True)
	friend_list_int = list(chain(friend_list_1, friend_list_2))
	friend_list = User.objects.filter(pk__in=friend_list_int)
	my_friend_list = []
	for a in friend_list:
		my_friend_list.append(a)
	my_friend_list.append(request.user)
	post_list = Post.objects.filter(user__in=my_friend_list).order_by('-time')

	mydict = dict()
	all_other_user = User.objects.exclude(pk=request.user.id)
	for other_user in all_other_user:
		if other_user.id in friend_list_int:
			continue		# already is my friend
		his_friend_list_1 = Friend.objects.filter(user1=other_user).values_list('user2', flat=True)
		his_friend_list_2 = Friend.objects.filter(user2=other_user).values_list('user1', flat=True)
		his_friend_list_int = list(chain(his_friend_list_1, his_friend_list_2))
		common_friend_num = len(set(friend_list_int).intersection(set(his_friend_list_int)))
		mydict[other_user.id] = common_friend_num
	rec_list_int = sorted(mydict, key=mydict.get, reverse=True)
	recommend_list = []
	i = 0
	for user_id in rec_list_int:
		if i > 2:
			break
		recommend_list.append(User.objects.get(pk=user_id))
		i = i + 1

	recent_pk_list = Visit.objects.filter(dst=request.user).order_by('-time').values_list('src', flat=True)
	recent_list = []
	i = 0
	for user_id in recent_pk_list:
		if i > 4:
			break
		recent_list.append(User.objects.get(pk=user_id))
		i = i + 1

	comment_list = Comment.objects.all().order_by('time')

	context = {'notice_list' : notice_list, 'post_list' : post_list, 'recommend_list' : recommend_list, 'request_list' : request_list, 'cur_user' : request.user, 'recent_list' : recent_list, 'comment_list' : comment_list}

	return render(request, 'bookface/home.html', context)

@login_required
def addpost(request):
	if 'picture' in request.FILES and request.POST['location_name']:
		new_post = Post(text=request.POST['post'], user=request.user, pic=request.FILES['picture'], 
		location=request.POST['location_name'], latitude=float(request.POST['latitude']), 
		longitude=float(request.POST['longitude']))
		new_post.save()
	if 'picture' in request.FILES and (not request.POST['location_name'] and not request.POST['latitude'] and not request.POST['longitude']):
		new_post = Post(text=request.POST['post'], user=request.user, pic=request.FILES['picture'])
		new_post.save()
	if 'picture' not in request.FILES and request.POST['location_name']:
		new_post = Post(text=request.POST['post'], user=request.user, 
			location=request.POST['location_name'], latitude=float(request.POST['latitude']), 
			longitude=float(request.POST['longitude']))
		new_post.save()
	if 'picture' not in request.FILES and (not request.POST['location_name'] and not request.POST['latitude'] and not request.POST['longitude']):
		new_post = Post(text=request.POST['post'], user=request.user)
		new_post.save()

	# new_post = Post(text=request.POST['post'], user=request.user)
	# new_post.save()

	notice_list = ['New post added.']

	friend_list_1 = Friend.objects.filter(user1=request.user).values_list('user2', flat=True)
	friend_list_2 = Friend.objects.filter(user2=request.user).values_list('user1', flat=True)
	friend_list_int = list(chain(friend_list_1, friend_list_2))
	friend_list = User.objects.filter(pk__in=friend_list_int)
	my_friend_list = []
	for a in friend_list:
		my_friend_list.append(a)
	my_friend_list.append(request.user)
	post_list = Post.objects.filter(user__in=my_friend_list).order_by('-time')

	mydict = dict()
	all_other_user = User.objects.exclude(pk=request.user.id)
	for other_user in all_other_user:
		if other_user.id in friend_list_int:
			continue		# already is my friend
		his_friend_list_1 = Friend.objects.filter(user1=other_user).values_list('user2', flat=True)
		his_friend_list_2 = Friend.objects.filter(user2=other_user).values_list('user1', flat=True)
		his_friend_list_int = list(chain(his_friend_list_1, his_friend_list_2))
		common_friend_num = len(set(friend_list_int).intersection(set(his_friend_list_int)))
		mydict[other_user.id] = common_friend_num
	rec_list_int = sorted(mydict, key=mydict.get, reverse=True)
	recommend_list = []
	i = 0
	for user_id in rec_list_int:
		if i > 2:
			break
		recommend_list.append(User.objects.get(pk=user_id))
		i = i + 1
	
	recent_pk_list = Visit.objects.filter(dst=request.user).order_by('-time').values_list('src', flat=True)
	recent_list = []
	i = 0
	for user_id in recent_pk_list:
		if i > 4:
			break
		recent_list.append(User.objects.get(pk=user_id))
		i = i + 1

	comment_list = Comment.objects.all().order_by('time')

	context = {'notice_list' : notice_list, 'post_list' : post_list, 'recommend_list' : recommend_list, 'cur_user' : request.user, 'recent_list' : recent_list, 'comment_list' : comment_list}

	return render(request, 'bookface/home.html', context)

def photo(request, id):
	post = get_object_or_404(Post, id=id)
	if not post.pic:
		raise Http404
	content_type = guess_type(post.pic.name)
	return HttpResponse(post.pic.read(), content_type=content_type)

def map(request, lat, lon):
	context = {}
	context['lat'] = lat
	context['lon'] = lon
	print lat
	print lon
	return render(request, 'bookface/googlemap.html', context)

@login_required
def listfriends(request):
	if 'unfriend' in request.GET:
		unfriend_username = request.GET['unfriend']
		unfriend_user = User.objects.get(username=unfriend_username)
		Friend.objects.filter(Q(user1=unfriend_user) | Q(user2=unfriend_user)).delete()

	friend_list_1 = Friend.objects.filter(user1=request.user).values_list('user2', flat=True)
	friend_list_2 = Friend.objects.filter(user2=request.user).values_list('user1', flat=True)
	friend_list_int = list(chain(friend_list_1, friend_list_2))
	friend_list = User.objects.filter(pk__in=friend_list_int)
	mydict = dict()
	all_other_user = User.objects.exclude(pk=request.user.id)
	for other_user in all_other_user:
		if other_user.id in friend_list_int:
			continue		# already is my friend
		his_friend_list_1 = Friend.objects.filter(user1=other_user).values_list('user2', flat=True)
		his_friend_list_2 = Friend.objects.filter(user2=other_user).values_list('user1', flat=True)
		his_friend_list_int = list(chain(his_friend_list_1, his_friend_list_2))
		common_friend_num = len(set(friend_list_int).intersection(set(his_friend_list_int)))
		mydict[other_user.id] = common_friend_num
	rec_list_int = sorted(mydict, key=mydict.get, reverse=True)
	recommend_list = []
	i = 0
	for user_id in rec_list_int:
		if i > 2:
			break
		recommend_list.append(User.objects.get(pk=user_id))
		i = i + 1

	recent_pk_list = Visit.objects.filter(dst=request.user).order_by('-time').values_list('src', flat=True)
	recent_list = []
	i = 0
	for user_id in recent_pk_list:
		if i > 4:
			break
		recent_list.append(User.objects.get(pk=user_id))
		i = i + 1

	context = {'friend_list' : friend_list, 'recommend_list' : recommend_list, 'cur_user' : request.user, 'recent_list' : recent_list}
	return render(request, 'bookface/friendlist.html', context)

@login_required
def visituser(request):
	dst_username = request.GET['username']
	dst_user = User.objects.get(username=dst_username)
	if dst_user == request.user:
		return redirect('/bookface/mypage')
	post_list = Post.objects.filter(user=dst_user).order_by('-time')
	Visit.objects.filter(src=request.user, dst=dst_user).delete()
	new_visit = Visit(src=request.user, dst=dst_user)
	new_visit.save()

	friend_list_1 = Friend.objects.filter(user1=request.user).values_list('user2', flat=True)
	friend_list_2 = Friend.objects.filter(user2=request.user).values_list('user1', flat=True)
	friend_list_int = list(chain(friend_list_1, friend_list_2))
	mydict = dict()
	all_other_user = User.objects.exclude(pk=request.user.id)
	for other_user in all_other_user:
		if other_user.id in friend_list_int:
			continue		# already is my friend
		his_friend_list_1 = Friend.objects.filter(user1=other_user).values_list('user2', flat=True)
		his_friend_list_2 = Friend.objects.filter(user2=other_user).values_list('user1', flat=True)
		his_friend_list_int = list(chain(his_friend_list_1, his_friend_list_2))
		common_friend_num = len(set(friend_list_int).intersection(set(his_friend_list_int)))
		mydict[other_user.id] = common_friend_num
	rec_list_int = sorted(mydict, key=mydict.get, reverse=True)
	recommend_list = []
	i = 0
	for user_id in rec_list_int:
		if i > 2:
			break
		recommend_list.append(User.objects.get(pk=user_id))
		i = i + 1

	recent_pk_list = Visit.objects.filter(dst=request.user).order_by('-time').values_list('src', flat=True)
	recent_list = []
	i = 0
	for user_id in recent_pk_list:
		if i > 4:
			break
		recent_list.append(User.objects.get(pk=user_id))
		i = i + 1

	comment_list = Comment.objects.all().order_by('time')

	if Friend.objects.filter(Q(user1=request.user, user2=dst_user) | Q(user1=dst_user, user2=request.user)).exists():
		is_friend = 1
	else:
		is_friend = 0

	context = {'post_list' : post_list, 'recommend_list' : recommend_list, 'cur_user' : request.user, 'dst_user' : dst_user, 'recent_list' : recent_list, 'comment_list' : comment_list, 'is_friend' : is_friend}
	return render(request, 'bookface/visituser.html', context)

@login_required
def share(request):
	post_id=request.GET['id']
	shared_post = Post.objects.get(pk=post_id)
	orig_user=shared_post.user
	new_post_text = 'Shared from ' + orig_user.first_name + ' ' + orig_user.last_name + ': ' + shared_post.text
	new_post = Post(text=new_post_text, user=request.user)
	new_post.save()

	friend_list_1 = Friend.objects.filter(user1=request.user).values_list('user2', flat=True)
	friend_list_2 = Friend.objects.filter(user2=request.user).values_list('user1', flat=True)
	friend_list_int = list(chain(friend_list_1, friend_list_2))
	friend_list = User.objects.filter(pk__in=friend_list_int)
	my_friend_list = []
	for a in friend_list:
		my_friend_list.append(a)
	my_friend_list.append(request.user)
	post_list = Post.objects.filter(user__in=my_friend_list).order_by('-time')

	mydict = dict()
	all_other_user = User.objects.exclude(pk=request.user.id)
	for other_user in all_other_user:
		if other_user.id in friend_list_int:
			continue		# already is my friend
		his_friend_list_1 = Friend.objects.filter(user1=other_user).values_list('user2', flat=True)
		his_friend_list_2 = Friend.objects.filter(user2=other_user).values_list('user1', flat=True)
		his_friend_list_int = list(chain(his_friend_list_1, his_friend_list_2))
		common_friend_num = len(set(friend_list_int).intersection(set(his_friend_list_int)))
		mydict[other_user.id] = common_friend_num
	rec_list_int = sorted(mydict, key=mydict.get, reverse=True)
	recommend_list = []
	i = 0
	for user_id in rec_list_int:
		if i > 2:
			break
		recommend_list.append(User.objects.get(pk=user_id))
		i = i + 1

	recent_pk_list = Visit.objects.filter(dst=request.user).order_by('-time').values_list('src', flat=True)
	recent_list = []
	i = 0
	for user_id in recent_pk_list:
		if i > 4:
			break
		recent_list.append(User.objects.get(pk=user_id))
		i = i + 1

	comment_list = Comment.objects.all().order_by('time')

	context = {'post_list' : post_list, 'recommend_list' : recommend_list, 'cur_user' : request.user, 'recent_list' : recent_list, 'comment_list' : comment_list}

	return render(request, 'bookface/home.html', context)

@login_required
def comment(request):
	post_id=request.GET['id']
	post = Post.objects.get(pk=post_id)
	

	friend_list_1 = Friend.objects.filter(user1=request.user).values_list('user2', flat=True)
	friend_list_2 = Friend.objects.filter(user2=request.user).values_list('user1', flat=True)
	friend_list_int = list(chain(friend_list_1, friend_list_2))
	mydict = dict()
	all_other_user = User.objects.exclude(pk=request.user.id)
	for other_user in all_other_user:
		if other_user.id in friend_list_int:
			continue		# already is my friend
		his_friend_list_1 = Friend.objects.filter(user1=other_user).values_list('user2', flat=True)
		his_friend_list_2 = Friend.objects.filter(user2=other_user).values_list('user1', flat=True)
		his_friend_list_int = list(chain(his_friend_list_1, his_friend_list_2))
		common_friend_num = len(set(friend_list_int).intersection(set(his_friend_list_int)))
		mydict[other_user.id] = common_friend_num
	rec_list_int = sorted(mydict, key=mydict.get, reverse=True)
	recommend_list = []
	i = 0
	for user_id in rec_list_int:
		if i > 2:
			break
		recommend_list.append(User.objects.get(pk=user_id))
		i = i + 1

	recent_pk_list = Visit.objects.filter(dst=request.user).order_by('-time').values_list('src', flat=True)
	recent_list = []
	i = 0
	for user_id in recent_pk_list:
		if i > 4:
			break
		recent_list.append(User.objects.get(pk=user_id))
		i = i + 1

	comment_list = Comment.objects.filter(post=post).order_by('time')

	context = {'cur_user' : request.user, 'post' : post, 'recommend_list' : recommend_list, 'recent_list' : recent_list, 'comment_list' : comment_list}
	return render(request, 'bookface/addcomment.html', context)

@login_required
def addcomment(request):
	post_id=request.POST['postid']
	comment_text = request.POST['comment']
	this_post = Post.objects.get(pk=post_id)
	new_comment = Comment(text=comment_text, post=this_post, src_user=request.user)
	new_comment.save()

	friend_list_1 = Friend.objects.filter(user1=request.user).values_list('user2', flat=True)
	friend_list_2 = Friend.objects.filter(user2=request.user).values_list('user1', flat=True)
	friend_list_int = list(chain(friend_list_1, friend_list_2))
	friend_list = User.objects.filter(pk__in=friend_list_int)
	my_friend_list = []
	for a in friend_list:
		my_friend_list.append(a)
	my_friend_list.append(request.user)
	post_list = Post.objects.filter(user__in=my_friend_list).order_by('-time')

	mydict = dict()
	all_other_user = User.objects.exclude(pk=request.user.id)
	for other_user in all_other_user:
		if other_user.id in friend_list_int:
			continue		# already is my friend
		his_friend_list_1 = Friend.objects.filter(user1=other_user).values_list('user2', flat=True)
		his_friend_list_2 = Friend.objects.filter(user2=other_user).values_list('user1', flat=True)
		his_friend_list_int = list(chain(his_friend_list_1, his_friend_list_2))
		common_friend_num = len(set(friend_list_int).intersection(set(his_friend_list_int)))
		mydict[other_user.id] = common_friend_num
	rec_list_int = sorted(mydict, key=mydict.get, reverse=True)
	recommend_list = []
	i = 0
	for user_id in rec_list_int:
		if i > 2:
			break
		recommend_list.append(User.objects.get(pk=user_id))
		i = i + 1
	
	recent_pk_list = Visit.objects.filter(dst=request.user).order_by('-time').values_list('src', flat=True)
	recent_list = []
	i = 0
	for user_id in recent_pk_list:
		if i > 4:
			break
		recent_list.append(User.objects.get(pk=user_id))
		i = i + 1

	comment_list = Comment.objects.all().order_by('time')

	context = {'cur_user' : request.user, 'post_list' : post_list, 'recommend_list' : recommend_list, 'recent_list' : recent_list, 'comment_list' : comment_list}
	return render(request, 'bookface/home.html', context)

@login_required
def mypage(request):
	post_list = Post.objects.filter(user=request.user).order_by('-time')
	
	friend_list_1 = Friend.objects.filter(user1=request.user).values_list('user2', flat=True)
	friend_list_2 = Friend.objects.filter(user2=request.user).values_list('user1', flat=True)
	friend_list_int = list(chain(friend_list_1, friend_list_2))
	mydict = dict()
	all_other_user = User.objects.exclude(pk=request.user.id)
	for other_user in all_other_user:
		if other_user.id in friend_list_int:
			continue		# already is my friend
		his_friend_list_1 = Friend.objects.filter(user1=other_user).values_list('user2', flat=True)
		his_friend_list_2 = Friend.objects.filter(user2=other_user).values_list('user1', flat=True)
		his_friend_list_int = list(chain(his_friend_list_1, his_friend_list_2))
		common_friend_num = len(set(friend_list_int).intersection(set(his_friend_list_int)))
		mydict[other_user.id] = common_friend_num
	rec_list_int = sorted(mydict, key=mydict.get, reverse=True)
	recommend_list = []
	i = 0
	for user_id in rec_list_int:
		if i > 2:
			break
		recommend_list.append(User.objects.get(pk=user_id))
		i = i + 1

	recent_pk_list = Visit.objects.filter(dst=request.user).order_by('-time').values_list('src', flat=True)
	recent_list = []
	i = 0
	for user_id in recent_pk_list:
		if i > 4:
			break
		recent_list.append(User.objects.get(pk=user_id))
		i = i + 1

	comment_list = Comment.objects.all().order_by('time')

	context = {'cur_user' : request.user, 'post_list' : post_list, 'recommend_list' : recommend_list, 'recent_list' : recent_list, 'comment_list' : comment_list}
	return render(request, 'bookface/mypage.html', context)

@login_required
def deletepost(request):
	post_id=request.GET['id']
	Post.objects.get(pk=post_id).delete()

	post_list = Post.objects.filter(user=request.user).order_by('-time')
	friend_list_1 = Friend.objects.filter(user1=request.user).values_list('user2', flat=True)
	friend_list_2 = Friend.objects.filter(user2=request.user).values_list('user1', flat=True)
	friend_list_int = list(chain(friend_list_1, friend_list_2))
	mydict = dict()
	all_other_user = User.objects.exclude(pk=request.user.id)
	for other_user in all_other_user:
		if other_user.id in friend_list_int:
			continue		# already is my friend
		his_friend_list_1 = Friend.objects.filter(user1=other_user).values_list('user2', flat=True)
		his_friend_list_2 = Friend.objects.filter(user2=other_user).values_list('user1', flat=True)
		his_friend_list_int = list(chain(his_friend_list_1, his_friend_list_2))
		common_friend_num = len(set(friend_list_int).intersection(set(his_friend_list_int)))
		mydict[other_user.id] = common_friend_num
	rec_list_int = sorted(mydict, key=mydict.get, reverse=True)
	recommend_list = []
	i = 0
	for user_id in rec_list_int:
		if i > 2:
			break
		recommend_list.append(User.objects.get(pk=user_id))
		i = i + 1

	recent_pk_list = Visit.objects.filter(dst=request.user).order_by('-time').values_list('src', flat=True)
	recent_list = []
	i = 0
	for user_id in recent_pk_list:
		if i > 4:
			break
		recent_list.append(User.objects.get(pk=user_id))
		i = i + 1

	comment_list = Comment.objects.all().order_by('time')

	context = {'cur_user' : request.user, 'post_list' : post_list, 'recommend_list' : recommend_list, 'recent_list' : recent_list, 'comment_list' : comment_list}
	return render(request, 'bookface/mypage.html', context)

@login_required
def sendmessage(request):
	dst_username = request.GET['username']
	dst_user = User.objects.get(username=dst_username)
	message_list = Message.objects.filter(Q(src=request.user, dst=dst_user) | Q(src=dst_user, dst=request.user)).order_by('time')
	
	friend_list_1 = Friend.objects.filter(user1=request.user).values_list('user2', flat=True)
	friend_list_2 = Friend.objects.filter(user2=request.user).values_list('user1', flat=True)
	friend_list_int = list(chain(friend_list_1, friend_list_2))
	mydict = dict()
	all_other_user = User.objects.exclude(pk=request.user.id)
	for other_user in all_other_user:
		if other_user.id in friend_list_int:
			continue		# already is my friend
		his_friend_list_1 = Friend.objects.filter(user1=other_user).values_list('user2', flat=True)
		his_friend_list_2 = Friend.objects.filter(user2=other_user).values_list('user1', flat=True)
		his_friend_list_int = list(chain(his_friend_list_1, his_friend_list_2))
		common_friend_num = len(set(friend_list_int).intersection(set(his_friend_list_int)))
		mydict[other_user.id] = common_friend_num
	rec_list_int = sorted(mydict, key=mydict.get, reverse=True)
	recommend_list = []
	i = 0
	for user_id in rec_list_int:
		if i > 2:
			break
		recommend_list.append(User.objects.get(pk=user_id))
		i = i + 1

	recent_pk_list = Visit.objects.filter(dst=request.user).order_by('-time').values_list('src', flat=True)
	recent_list = []
	i = 0
	for user_id in recent_pk_list:
		if i > 4:
			break
		recent_list.append(User.objects.get(pk=user_id))
		i = i + 1

	context = {'cur_user' : request.user, 'dst_user' : dst_user, 'message_list' : message_list, 'recommend_list' : recommend_list, 'recent_list' : recent_list}
	return render(request, 'bookface/sendmessage.html', context)

@login_required
def dosend(request):
	text = request.POST['msg']
	dst_username = request.POST['username']
	dst_user = User.objects.get(username=dst_username)
	new_message = Message(text=text, src=request.user, dst=dst_user)
	new_message.save()

	message_list = Message.objects.filter(Q(src=request.user, dst=dst_user) | Q(src=dst_user, dst=request.user)).order_by('time')
	friend_list_1 = Friend.objects.filter(user1=request.user).values_list('user2', flat=True)
	friend_list_2 = Friend.objects.filter(user2=request.user).values_list('user1', flat=True)
	friend_list_int = list(chain(friend_list_1, friend_list_2))
	mydict = dict()
	all_other_user = User.objects.exclude(pk=request.user.id)
	for other_user in all_other_user:
		if other_user.id in friend_list_int:
			continue		# already is my friend
		his_friend_list_1 = Friend.objects.filter(user1=other_user).values_list('user2', flat=True)
		his_friend_list_2 = Friend.objects.filter(user2=other_user).values_list('user1', flat=True)
		his_friend_list_int = list(chain(his_friend_list_1, his_friend_list_2))
		common_friend_num = len(set(friend_list_int).intersection(set(his_friend_list_int)))
		mydict[other_user.id] = common_friend_num
	rec_list_int = sorted(mydict, key=mydict.get, reverse=True)
	recommend_list = []
	i = 0
	for user_id in rec_list_int:
		if i > 2:
			break
		recommend_list.append(User.objects.get(pk=user_id))
		i = i + 1

	recent_pk_list = Visit.objects.filter(dst=request.user).order_by('-time').values_list('src', flat=True)
	recent_list = []
	i = 0
	for user_id in recent_pk_list:
		if i > 4:
			break
		recent_list.append(User.objects.get(pk=user_id))
		i = i + 1

	context = {'cur_user' : request.user, 'dst_user' : dst_user, 'message_list' : message_list, 'recommend_list' : recommend_list, 'recent_list' : recent_list}
	return render(request, 'bookface/sendmessage.html', context)

@login_required
def messagecenter(request):
	message_list = Message.objects.filter(Q(src=request.user) | Q(dst=request.user)).order_by('time')
	user_list = []
	for message in message_list:
		if message.src == request.user:
			user_list.append(message.dst)
		elif message.dst == request.user:
			user_list.append(message.src)
	unique_user_list = list(set(user_list))

	friend_list_1 = Friend.objects.filter(user1=request.user).values_list('user2', flat=True)
	friend_list_2 = Friend.objects.filter(user2=request.user).values_list('user1', flat=True)
	friend_list_int = list(chain(friend_list_1, friend_list_2))
	mydict = dict()
	all_other_user = User.objects.exclude(pk=request.user.id)
	for other_user in all_other_user:
		if other_user.id in friend_list_int:
			continue		# already is my friend
		his_friend_list_1 = Friend.objects.filter(user1=other_user).values_list('user2', flat=True)
		his_friend_list_2 = Friend.objects.filter(user2=other_user).values_list('user1', flat=True)
		his_friend_list_int = list(chain(his_friend_list_1, his_friend_list_2))
		common_friend_num = len(set(friend_list_int).intersection(set(his_friend_list_int)))
		mydict[other_user.id] = common_friend_num
	rec_list_int = sorted(mydict, key=mydict.get, reverse=True)
	recommend_list = []
	i = 0
	for user_id in rec_list_int:
		if i > 2:
			break
		recommend_list.append(User.objects.get(pk=user_id))
		i = i + 1

	recent_pk_list = Visit.objects.filter(dst=request.user).order_by('-time').values_list('src', flat=True)
	recent_list = []
	i = 0
	for user_id in recent_pk_list:
		if i > 4:
			break
		recent_list.append(User.objects.get(pk=user_id))
		i = i + 1

	context = {'cur_user' : request.user, 'recommend_list' : recommend_list, 'recent_list' : recent_list, 'message_list' : message_list, 'user_list' : unique_user_list}
	return render(request, "bookface/messagecenter.html", context)

@login_required
def searchuser(request):
	keyword_string = request.POST['keyword']
	keywords = keyword_string.lower().split(' ')
	all_users = User.objects.all()
	valid_users = []
	for word in keywords:
		for user in all_users:
			if user.first_name.lower().find(word) > -1 or user.last_name.lower().find(word) > -1:
				valid_users.append(user)
	user_list = list(set(valid_users))

	friend_list_1 = Friend.objects.filter(user1=request.user).values_list('user2', flat=True)
	friend_list_2 = Friend.objects.filter(user2=request.user).values_list('user1', flat=True)
	friend_list_int = list(chain(friend_list_1, friend_list_2))
	mydict = dict()
	all_other_user = User.objects.exclude(pk=request.user.id)
	for other_user in all_other_user:
		if other_user.id in friend_list_int:
			continue		# already is my friend
		his_friend_list_1 = Friend.objects.filter(user1=other_user).values_list('user2', flat=True)
		his_friend_list_2 = Friend.objects.filter(user2=other_user).values_list('user1', flat=True)
		his_friend_list_int = list(chain(his_friend_list_1, his_friend_list_2))
		common_friend_num = len(set(friend_list_int).intersection(set(his_friend_list_int)))
		mydict[other_user.id] = common_friend_num
	rec_list_int = sorted(mydict, key=mydict.get, reverse=True)
	recommend_list = []
	i = 0
	for user_id in rec_list_int:
		if i > 2:
			break
		recommend_list.append(User.objects.get(pk=user_id))
		i = i + 1

	recent_pk_list = Visit.objects.filter(dst=request.user).order_by('-time').values_list('src', flat=True)
	recent_list = []
	i = 0
	for user_id in recent_pk_list:
		if i > 4:
			break
		recent_list.append(User.objects.get(pk=user_id))
		i = i + 1

	context = {'cur_user' : request.user, 'recommend_list' : recommend_list, 'recent_list' : recent_list, 'user_list' : user_list}
	return render(request, 'bookface/searchuser.html', context)

@login_required
def searchpost(request):
	keyword_string = request.POST['keyword']
	keywords = keyword_string.lower().split(' ')
	all_posts = Post.objects.all()
	valid_posts = []
	for word in keywords:
		for post in all_posts:
			if post.text.lower().find(word) > -1:
				valid_posts.append(post)
	post_list = list(set(valid_posts))

	friend_list_1 = Friend.objects.filter(user1=request.user).values_list('user2', flat=True)
	friend_list_2 = Friend.objects.filter(user2=request.user).values_list('user1', flat=True)
	friend_list_int = list(chain(friend_list_1, friend_list_2))

	mydict = dict()
	all_other_user = User.objects.exclude(pk=request.user.id)
	for other_user in all_other_user:
		if other_user.id in friend_list_int:
			continue		# already is my friend
		his_friend_list_1 = Friend.objects.filter(user1=other_user).values_list('user2', flat=True)
		his_friend_list_2 = Friend.objects.filter(user2=other_user).values_list('user1', flat=True)
		his_friend_list_int = list(chain(his_friend_list_1, his_friend_list_2))
		common_friend_num = len(set(friend_list_int).intersection(set(his_friend_list_int)))
		mydict[other_user.id] = common_friend_num
	rec_list_int = sorted(mydict, key=mydict.get, reverse=True)
	recommend_list = []
	i = 0
	for user_id in rec_list_int:
		if i > 2:
			break
		recommend_list.append(User.objects.get(pk=user_id))
		i = i + 1

	recent_pk_list = Visit.objects.filter(dst=request.user).order_by('-time').values_list('src', flat=True)
	recent_list = []
	i = 0
	for user_id in recent_pk_list:
		if i > 4:
			break
		recent_list.append(User.objects.get(pk=user_id))
		i = i + 1

	comment_list = Comment.objects.all().order_by('time')

	context = {'cur_user' : request.user, 'recommend_list' : recommend_list, 'recent_list' : recent_list, 'post_list' : post_list, 'comment_list' : comment_list}
	return render(request, 'bookface/searchpost.html', context)

@login_required
def search(request):
	friend_list_1 = Friend.objects.filter(user1=request.user).values_list('user2', flat=True)
	friend_list_2 = Friend.objects.filter(user2=request.user).values_list('user1', flat=True)
	friend_list_int = list(chain(friend_list_1, friend_list_2))
	mydict = dict()
	all_other_user = User.objects.exclude(pk=request.user.id)
	for other_user in all_other_user:
		if other_user.id in friend_list_int:
			continue		# already is my friend
		his_friend_list_1 = Friend.objects.filter(user1=other_user).values_list('user2', flat=True)
		his_friend_list_2 = Friend.objects.filter(user2=other_user).values_list('user1', flat=True)
		his_friend_list_int = list(chain(his_friend_list_1, his_friend_list_2))
		common_friend_num = len(set(friend_list_int).intersection(set(his_friend_list_int)))
		mydict[other_user.id] = common_friend_num
	rec_list_int = sorted(mydict, key=mydict.get, reverse=True)
	recommend_list = []
	i = 0
	for user_id in rec_list_int:
		if i > 2:
			break
		recommend_list.append(User.objects.get(pk=user_id))
		i = i + 1

	recent_pk_list = Visit.objects.filter(dst=request.user).order_by('-time').values_list('src', flat=True)
	recent_list = []
	i = 0
	for user_id in recent_pk_list:
		if i > 4:
			break
		recent_list.append(User.objects.get(pk=user_id))
		i = i + 1

	context = {'cur_user' : request.user, 'recommend_list' : recommend_list, 'recent_list' : recent_list}
	return render(request, 'bookface/search.html', context)

@login_required
def hottopic(request):
	posts = Post.objects.all()
	dictionary = dict()
	for post in posts:
		word_list = post.text.lower().split(' ')
		for word in word_list:
			clean_word = word.strip(',.?!:#')
			if len(clean_word) < 5:
				continue
			if clean_word not in dictionary:
				dictionary[clean_word] = 1
			else:
				value = dictionary.get(clean_word)
				dictionary[clean_word] = value + 1
	key_list = sorted(dictionary, key=dictionary.get, reverse=True)
	keyword_list = []
	i = 0
	for keyword in key_list:
		if i > 4:
			break
		keyword_list.append(keyword)
		i = i + 1

	friend_list_1 = Friend.objects.filter(user1=request.user).values_list('user2', flat=True)
	friend_list_2 = Friend.objects.filter(user2=request.user).values_list('user1', flat=True)
	friend_list_int = list(chain(friend_list_1, friend_list_2))
	mydict = dict()
	all_other_user = User.objects.exclude(pk=request.user.id)
	for other_user in all_other_user:
		if other_user.id in friend_list_int:
			continue		# already is my friend
		his_friend_list_1 = Friend.objects.filter(user1=other_user).values_list('user2', flat=True)
		his_friend_list_2 = Friend.objects.filter(user2=other_user).values_list('user1', flat=True)
		his_friend_list_int = list(chain(his_friend_list_1, his_friend_list_2))
		common_friend_num = len(set(friend_list_int).intersection(set(his_friend_list_int)))
		mydict[other_user.id] = common_friend_num
	rec_list_int = sorted(mydict, key=mydict.get, reverse=True)
	recommend_list = []
	i = 0
	for user_id in rec_list_int:
		if i > 2:
			break
		recommend_list.append(User.objects.get(pk=user_id))
		i = i + 1

	recent_pk_list = Visit.objects.filter(dst=request.user).order_by('-time').values_list('src', flat=True)
	recent_list = []
	i = 0
	for user_id in recent_pk_list:
		if i > 4:
			break
		recent_list.append(User.objects.get(pk=user_id))
		i = i + 1

	comment_list = Comment.objects.all().order_by('time')

	context = {'cur_user' : request.user, 'recommend_list' : recommend_list, 'recent_list' : recent_list, 'post_list' : posts, 'keyword_list' : keyword_list, 'comment_list' : comment_list}
	return render(request, 'bookface/hottopic.html', context)

@login_required
def gallery(request):
	posts = Post.objects.all().order_by('-time')
	post_list = []
	for post in posts:
		if post.pic:
			post_list.append(post)

	friend_list_1 = Friend.objects.filter(user1=request.user).values_list('user2', flat=True)
	friend_list_2 = Friend.objects.filter(user2=request.user).values_list('user1', flat=True)
	friend_list_int = list(chain(friend_list_1, friend_list_2))
	mydict = dict()
	all_other_user = User.objects.exclude(pk=request.user.id)
	for other_user in all_other_user:
		if other_user.id in friend_list_int:
			continue		# already is my friend
		his_friend_list_1 = Friend.objects.filter(user1=other_user).values_list('user2', flat=True)
		his_friend_list_2 = Friend.objects.filter(user2=other_user).values_list('user1', flat=True)
		his_friend_list_int = list(chain(his_friend_list_1, his_friend_list_2))
		common_friend_num = len(set(friend_list_int).intersection(set(his_friend_list_int)))
		mydict[other_user.id] = common_friend_num
	rec_list_int = sorted(mydict, key=mydict.get, reverse=True)
	recommend_list = []
	i = 0
	for user_id in rec_list_int:
		if i > 2:
			break
		recommend_list.append(User.objects.get(pk=user_id))
		i = i + 1

	recent_pk_list = Visit.objects.filter(dst=request.user).order_by('-time').values_list('src', flat=True)
	recent_list = []
	i = 0
	for user_id in recent_pk_list:
		if i > 4:
			break
		recent_list.append(User.objects.get(pk=user_id))
		i = i + 1

	comment_list = Comment.objects.all().order_by('time')

	context = {'cur_user' : request.user, 'recommend_list' : recommend_list, 'recent_list' : recent_list, 'post_list' : post_list, 'comment_list' : comment_list}
	return render(request, 'bookface/gallery.html', context)

def register(request):
	context = {}
	if request.method == 'GET':
		return render(request, 'bookface/register.html', context)
	errors = []
	context['errors'] = errors

	new_user = User.objects.create_user(username=request.POST['username'], \
                                        password=request.POST['password'], \
										first_name=request.POST['firstname'], \
										last_name=request.POST['lastname'])
	new_user.is_active = True
	new_user.save()
	
	return redirect('/bookface/login')
