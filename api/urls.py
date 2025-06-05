from django.urls import path, include
from .views import SendZaloMessageView
urlpatterns = [
    path('api/auto-zalo/', SendZaloMessageView.as_view()),
]
