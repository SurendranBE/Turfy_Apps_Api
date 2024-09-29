from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from knox.models import AuthToken
from .serializers import *
from .models import OTP, Turf
from django.core.mail import send_mail
import random
from rest_framework import generics
from haversine import haversine



def serialize_user(user):
    return {
        "user_id" : user.id,
        "username": user.username,
        "email": user.email,
    }

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, email=email, password=password)
    if user is not None:
        _, token = AuthToken.objects.create(user)
        return Response({
            'user_data': serialize_user(user),
            'token': token
        })
    return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
        return Response({
            'status' : "success",
            'message' : "User Registered Successfully"
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    user = request.user
    if user.is_authenticated:
        return Response({
            'user_data': serialize_user(user)
        })
    return Response({"error": "User not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)

# this for password change 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Password changed successfully"})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#EMIL SEND OTP PASSWORD CHANGE PART

def generate_otp():
    return str(random.randint(1000, 9999))

def send_otp_email(email, otp):
    send_mail(
        'Your OTP Code',
        f'Your OTP code is {otp}',
        'mts85715@gmail.com',
        [email],
        fail_silently=False,
    )

@api_view(['POST'])
def request_otp(request):
    serializer = RequestOTPSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        otp = generate_otp()
        OTP.objects.create(user=user, otp=otp)
        send_otp_email(user.email, otp)

        return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    if serializer.is_valid():
        otp = serializer.validated_data['otp']

        try:
            otp_entry = OTP.objects.get(otp=otp)
        except OTP.DoesNotExist:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        if otp_entry.is_expired():
            return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)
        
        request.session['user_id'] = otp_entry.user.id
        otp_entry.delete()  # Delete OTP after successful verification

        return Response({"message": "OTP verified.", "user_id": otp_entry.user.id}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def reset_password(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return Response({"error": "User not verified."}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()

        del request.session['user_id']

        return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#PRODUCT ADD PAGE

@api_view(['POST'])
def turf_create(request):
    serializer = TurfSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def turfs_nearby(request):

    lat = request.query_params.get('latitude')
    lon = request.query_params.get('longitude')

    if lat is None or lon is None:
        return Response({'error': 'Latitude and longitude are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        reference_lat = float(lat)
        reference_lon = float(lon)
    except ValueError:
        return Response({'error': 'Invalid latitude or longitude'}, status=status.HTTP_400_BAD_REQUEST)

    reference_point = (reference_lat, reference_lon)

    nearby_turfs = []
    for turf in Turf.objects.all():
        turf_lat = turf.latitude_float
        turf_lon = turf.longitude_float
        if turf_lat is not None and turf_lon is not None:
            turf_point = (turf_lat, turf_lon)
            distance = haversine(reference_point, turf_point)
            if distance <= 10:
                nearby_turfs.append(turf)
            else:
                return Response({"message": "No Turf For your Loction"})

    serializer = TurfSerializer(nearby_turfs, many=True)
    return Response(serializer.data)

