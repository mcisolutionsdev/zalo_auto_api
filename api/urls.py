from django.urls import path, include
from .views import SendZaloMessageView, home
urlpatterns = [
    path('api/auto-zalo/', SendZaloMessageView.as_view()),
     path('',home,name="home"),

]
