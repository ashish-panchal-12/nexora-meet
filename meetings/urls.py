from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',              views.dashboard,      name='dashboard'),
    path('create/',                 views.create_meeting, name='create_meeting'),
    path('join/',                   views.join_meeting,   name='join_meeting'),
    path('room/<str:meeting_id>/',  views.room,           name='room'),
    path('end/<str:meeting_id>/',   views.end_meeting,    name='end_meeting'),
    path('delete/<str:meeting_id>/',views.delete_meeting, name='delete_meeting'),
    path('api/<str:meeting_id>/',   views.meeting_api,    name='meeting_api'),
]