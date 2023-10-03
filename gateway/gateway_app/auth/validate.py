import requests
import os
from django.views import View
from django.http import JsonResponse



    
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
