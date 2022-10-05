from django.urls import path
from django.urls import include

urlpatterns = [
    path('api/', include('nosql_objects.urls')),
]