import re
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from .serializers import RegisterSerializer
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import SearchQuery
from groq import Groq   
import requests

def login_page(request):
    return render(request, "core/login_page.html")

def signup_page(request):
    return render(request, "core/sign_up.html")



def is_strong_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True


@api_view(["POST"])
def register_user(request):

    email = request.data.get("email")
    password = request.data.get("password")

    if User.objects.filter(email=email).exists():
        return Response(
            {"error": "User already exists"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not is_strong_password(password):
        return Response(
            {"error": "Password must contain uppercase, lowercase, number, symbol and be at least 8 characters"},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully"}, status=201)

    return Response(serializer.errors, status=400)

@api_view(["POST"])
def login_user(request):

    email = request.data.get("email")
    password = request.data.get("password")

    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User does not exist"}, status=401)

    user = authenticate(username=user_obj.username, password=password)

    if user is not None:
        login(request, user)   # IMPORTANT

        return Response({
            "message": "Login successful",
            "username": user.username,
            "user_id": user.id
        })

    return Response({"error": "Invalid email or password"}, status=401)



@login_required(login_url="/login/")
def home_page(request):
    return render(request, "core/home_page.html", {
        "username": request.user.username
    })

@csrf_exempt
def search_api(request):
    if request.method == "POST":

        data = json.loads(request.body)
        query = data.get("query")

        search = SearchQuery.objects.create(
            user=request.user,
            query_text=query,
            category="general",
            session_id="session1",
            source_used="groq"
        )

        client = Groq(api_key=settings.GROQ_API_KEY)
        chat = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": query}]
        )
        answer = chat.choices[0].message.content

        search.answer_text = answer
        search.save()

        # YouTube fetch
        yt_response = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "q": query,
                "maxResults": 10,
                "type": "video",
                "key": settings.YOUTUBE_API_KEY
            }
        )
        yt_data = yt_response.json()

        # get all video ids
        video_ids = [item["id"]["videoId"] for item in yt_data.get("items", [])]

        # check which ones are actually embeddable
        details_response = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "status,snippet",
                "id": ",".join(video_ids),
                "key": settings.YOUTUBE_API_KEY
            }
        )
        details_data = details_response.json()
        print(details_data)

        # only keep embeddable ones, take first 2
        videos = []
        for item in details_data.get("items", []):
            if item["status"]["embeddable"] == True:
                videos.append({
                    "video_id": item["id"],
                    "title": item["snippet"]["title"]
                })
            if len(videos) == 2:
                break

        return JsonResponse({
            "status": "success",
            "query": query,
            "answer": answer,
            "videos": videos
        })