from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'bookface.views.home'),
	url(r'^home$', 'bookface.views.home'),
	url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'bookface/login.html'}),
	url(r'^logout$', 'django.contrib.auth.views.logout_then_login'),
	url(r'^register$', 'bookface.views.register'),
	url(r'^addpost$', 'bookface.views.addpost'),
	url(r'^listfriends$', 'bookface.views.listfriends'),
	url(r'^visituser$', 'bookface.views.visituser'),
	url(r'^share$', 'bookface.views.share'),
	url(r'^comment$', 'bookface.views.comment'),
	url(r'^addcomment$', 'bookface.views.addcomment'),
	url(r'^mypage$', 'bookface.views.mypage'),
	url(r'^deletepost$', 'bookface.views.deletepost'),
	url(r'^sendmessage$', 'bookface.views.sendmessage'),
	url(r'^dosend$', 'bookface.views.dosend'),
	url(r'^messagecenter$', 'bookface.views.messagecenter'),
	url(r'^searchuser$', 'bookface.views.searchuser'),
	url(r'^searchpost$', 'bookface.views.searchpost'),
	url(r'^search$', 'bookface.views.search'),
	url(r'^hottopic$', 'bookface.views.hottopic'),
	url(r'^photo/(?P<id>\d+)$', 'bookface.views.photo'),
	url(r'^map/(?P<lat>[-+]?[0-9]*.[0-9]*)a(?P<lon>[-+]?[0-9]*.[0-9]*)$','bookface.views.map'),
	url(r'^gallery$', 'bookface.views.gallery'),
)
