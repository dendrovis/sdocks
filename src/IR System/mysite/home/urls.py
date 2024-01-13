#==============================================================
# Course Name : Information Retrieval
# Course Code : CZ4034
# Title       : Information Retrieval Assignment (Group Project)
# Topic       : Stock Search
#==============================================================
from django.urls import path    # Django's URL function
from . import views             # Control which logics to execute to return the right template

# Define URL App level
urlpatterns = [
    path('', views.index, name='index'), # name is just for verbose
]