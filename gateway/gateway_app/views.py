from django.shortcuts import render
import requests
import os
from django.views import View
from django.http import JsonResponse, HttpResponse
from gridfs import GridFS
from pymongo import MongoClient
from bson import ObjectId
import pika
import json
from .auth import validate


class LoginView(View):
    def post(self, request):
        username = request.POST.get('email')
        password = request.POST.get('password')

        if not (username and password):
            return JsonResponse({"message": "missing credentials"}, status=401)

        response = requests.post(
            f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login", auth=(username, password)
        )

        if response.status_code == 200:
            token = response.text
            return JsonResponse({"message": token}, status=200)
        else:
            error_message = response.text
            status_code = response.status_code
            return JsonResponse({"message": error_message}, status=status_code)


class UploadView(View):
    def post(self, request):
        acc, err = validate.validationView(request)

        if err:
            return err

        if not request.FILES or len(request.FILES) != 1:
            return JsonResponse({"message": "exactly 1 file required"}, status=400)

        uploaded_file = request.FILES['file']

        client = MongoClient("mongodb://host.minikube.internal:27017")
        db = client["video"]
        fs = GridFS(db)

        try:
            file_id = fs.put(uploaded_file, filename=uploaded_file.name)
        except Exception as e:
            print(e)
            return JsonResponse({"message": "internal server error"}, status=500)

        channel = self.get_rabbitmq_channel()
        if channel:
            message = {
                "video_fid": str(file_id),
                "mp3_fid": None,
                "username": acc['username'],
            }
            channel.basic_publish(
                exchange="",
                routing_key="video",
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                ),
            )

        return JsonResponse({"message": "success!"}, status=200)

    def get_rabbitmq_channel(self):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
            return connection.channel()
        except Exception as e:
            print(e)
            return None


class DownloadView(View):
    def get(self, request):
        acc, err = validate.validationView(request)

        if err:
            return err

        fid_string = request.GET.get("fid")

        if not fid_string:
            return JsonResponse({"message": "fid is required"}, status=400)

        try:
            client = MongoClient("mongodb://host.minikube.internal:27017")
            db = client["mp3"]
            fs = GridFS(db)

            file_object = fs.get(ObjectId(fid_string))

            response = HttpResponse(file_object.read(), content_type="application/octet-stream")
            response["Content-Disposition"] = f'attachment; filename="{fid_string}.mp3"'

            return response
        except Exception as err:
            print(err)
            return JsonResponse({"message": "internal server error"}, status=500)

    def validationView(request):
        encoded_jwt = request.headers.get("Authorization")

        if not encoded_jwt:
            return None, ("missing credentials", 401)

        token = encoded_jwt.split(" ")[1]
        response = requests.post(
            f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
            headers={"Authorization": token},
        )

        if response.status_code == 200:
            return response.text, None
        else:
            return None, (response.text, response.status_code)
