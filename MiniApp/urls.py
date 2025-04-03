from django.urls import path
from . import views

urlpatterns = [
	path('', views.fileupload, name = "File_Uploads")
]
