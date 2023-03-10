from django.urls import path

from . import views

app_name = "RMC"


urlpatterns = [
    #Leave as empty string for base url
	path('', views.home, name="home"),
]
