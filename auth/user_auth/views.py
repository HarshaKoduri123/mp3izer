from django.shortcuts import render

from django.http import JsonResponse
from django.views import View
from django.contrib.auth.hashers import check_password
import jwt
import datetime
from decouple import config
import os
import json
from .models import User


class LoginView(View):

    def post(self, request):
        json_data = request.body.decode('utf-8')
        username=request.POST.get('email')
        password=request.POST.get('password')
        print(username,password)

        if not (username and password):
            return JsonResponse({"message": "missing credentials"}, status=401)

        try:

            user = User.objects.get(username=username)
            if user.username != username or user.password != password:
                return JsonResponse({"message": "invalid credentials"}, status=401)
            
            else:
                token = jwt.encode(
                {
                    "username": user.username,
                    "admin": True,
                },
                config("JWT_SECRET"),
                algorithm="HS256",
            )
            

        except User.DoesNotExist:
            return JsonResponse({"message": "User Not Found"}, status=401)
        

        return JsonResponse({"message": token}, status=401)

class ValidateView(View):
    
    def post(self, request):
        encoded_jwt = request.headers.get("Authorization")
        
        if not encoded_jwt:
            return JsonResponse({"message": "missing credentials"}, status=401)

        encoded_jwt = encoded_jwt.split(" ")[1]
     

        try:
            decoded = jwt.decode(
                encoded_jwt, config("JWT_SECRET"), algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return JsonResponse({"message": "token has expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"message": "invalid token"}, status=401)

        return JsonResponse({"message": decoded}, status=200)
