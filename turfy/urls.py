from django.urls import path
from .views import (
    register, 
    login, 
    get_user, 
    change_password, 
    request_otp, 
    verify_otp, 
    reset_password,
    turf_create, 
    turfs_nearby,
    
)
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('get_user/', get_user, name='get_user'),
    path('change_password/', change_password, name='change_password'),
    path('forgot_password/', request_otp, name='request-otp'),
    path('validate_otp/', verify_otp, name='verify-otp'),
    path('new_password/', reset_password, name='reset-password'),
    path('turfy_details/', turf_create, name='create_turf'),
    path('get_turfy', turfs_nearby, name='get_turfy'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
