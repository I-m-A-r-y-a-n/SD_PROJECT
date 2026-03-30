# import re
# from django.contrib.auth.models import User
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
# from django.contrib.auth import authenticate, login
# from .serializers import RegisterSerializer
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# import json
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.conf import settings
# from .models import SearchQuery
# from groq import Groq
# import requests
# from serpapi import GoogleSearch
# from django.contrib.auth import logout

# def login_page(request):
#     return render(request, "core/login_page.html")

# def signup_page(request):
#     return render(request, "core/sign_up.html")

# def is_strong_password(password):
#     if len(password) < 8:
#         return False
#     if not re.search(r"[A-Z]", password):
#         return False
#     if not re.search(r"[a-z]", password):
#         return False
#     if not re.search(r"[0-9]", password):
#         return False
#     if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
#         return False
#     return True

# @api_view(["POST"])
# def register_user(request):
#     email = request.data.get("email")
#     password = request.data.get("password")
#     if User.objects.filter(email=email).exists():
#         return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
#     if not is_strong_password(password):
#         return Response({"error": "Password must contain uppercase, lowercase, number, symbol and be at least 8 characters"}, status=status.HTTP_400_BAD_REQUEST)
#     serializer = RegisterSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response({"message": "User registered successfully"}, status=201)
#     return Response(serializer.errors, status=400)

# @api_view(["POST"])
# def login_user(request):
#     email = request.data.get("email")
#     password = request.data.get("password")
#     try:
#         user_obj = User.objects.get(email=email)
#     except User.DoesNotExist:
#         return Response({"error": "User does not exist"}, status=401)
#     user = authenticate(username=user_obj.username, password=password)
#     if user is not None:
#         login(request, user)
#         return Response({"message": "Login successful", "username": user.username, "user_id": user.id})
#     return Response({"error": "Invalid email or password"}, status=401)

# @login_required(login_url="/login/")
# def home_page(request):
#     return render(request, "core/home_page.html", {"username": request.user.username})

# @csrf_exempt
# def search_api(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         query = data.get("query")

#         search = SearchQuery.objects.create(
#             user=request.user,
#             query_text=query,
#             category="general",
#             session_id="session1",
#             source_used="groq"
#         )

#         # GROQ
#         client = Groq(api_key=settings.GROQ_API_KEY)
#         chat = client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": query}]
#         )
#         answer = chat.choices[0].message.content
#         search.answer_text = answer

#         # YouTube
#         yt_response = requests.get(
#             "https://www.googleapis.com/youtube/v3/search",
#             params={"part": "snippet", "q": query, "maxResults": 10, "type": "video", "key": settings.YOUTUBE_API_KEY}
#         )
#         yt_data = yt_response.json()
#         video_ids = [item["id"]["videoId"] for item in yt_data.get("items", [])]
#         details_response = requests.get(
#             "https://www.googleapis.com/youtube/v3/videos",
#             params={"part": "status,snippet", "id": ",".join(video_ids), "key": settings.YOUTUBE_API_KEY}
#         )
#         details_data = details_response.json()
#         videos = []
#         for item in details_data.get("items", []):
#             if item["status"]["embeddable"] == True:
#                 videos.append({"video_id": item["id"], "title": item["snippet"]["title"]})
#             if len(videos) == 2:
#                 break

#         # SERP
#         serp_search = GoogleSearch({"q": query, "api_key": settings.SERP_API_KEY, "num": 5})
#         serp_results = serp_search.get_dict()
#         links = []
#         for result in serp_results.get("organic_results", [])[:5]:
#             links.append({
#                 "title": result.get("title", ""),
#                 "url": result.get("link", ""),
#                 "snippet": result.get("snippet", "")
#             })

#         # save everything
#         search.videos_json = json.dumps(videos)
#         search.links_json = json.dumps(links)
#         search.save()

#         return JsonResponse({
#             "status": "success",
#             "query": query,
#             "answer": answer,
#             "videos": videos,
#             "links": links
#         })

# @csrf_exempt
# def history_api(request):
#     if request.method == "GET":
#         searches = SearchQuery.objects.filter(
#             user=request.user
#         ).order_by("-created_at")[:20]

#         history = []
#         for s in searches:
#             history.append({
#                 "query": s.query_text,
#                 "answer": s.answer_text,
#                 "videos": json.loads(s.videos_json) if s.videos_json else [],
#                 "links": json.loads(s.links_json) if s.links_json else [],
#                 "created_at": s.created_at.strftime("%d %b %Y, %I:%M %p")
#             })

#         return JsonResponse({"history": history})


# @csrf_exempt
# def logout_user(request):
#     logout(request)
#     return JsonResponse({"message": "Logged out"})

import re
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from .serializers import RegisterSerializer
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import SearchQuery, Source, Content, Topic, Category
from groq import Groq
import requests
from serpapi import GoogleSearch

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
        return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
    if not is_strong_password(password):
        return Response({"error": "Password must contain uppercase, lowercase, number, symbol and be at least 8 characters"}, status=status.HTTP_400_BAD_REQUEST)
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
        login(request, user)
        return Response({"message": "Login successful", "username": user.username, "user_id": user.id})
    return Response({"error": "Invalid email or password"}, status=401)

@login_required(login_url="/login/")
def home_page(request):
    return render(request, "core/home_page.html", {"username": request.user.username})

@csrf_exempt
def search_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        query = data.get("query")

        # get or create category and topic
        category_obj, _ = Category.objects.get_or_create(category_name="General")
        topic_obj, _ = Topic.objects.get_or_create(
            topic_name=query[:80],
            defaults={"category": category_obj}
        )

        search = SearchQuery.objects.create(
            user=request.user,
            query_text=query,
            category="general",
            session_id="session1",
            source_used="groq",
            topic=topic_obj
        )

        # GROQ
        client = Groq(api_key=settings.GROQ_API_KEY)
        chat = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": query}]
        )
        answer = chat.choices[0].message.content
        search.answer_text = answer

        # YouTube
        yt_response = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={"part": "snippet", "q": query, "maxResults": 20, "type": "video", "key": settings.YOUTUBE_API_KEY}
        )
        yt_data = yt_response.json()
        video_ids = [item["id"]["videoId"] for item in yt_data.get("items", []) if item["id"].get("videoId")]
        details_response = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={"part": "status,snippet", "id": ",".join(video_ids), "key": settings.YOUTUBE_API_KEY}
        )
        details_data = details_response.json()
        videos = []
        for item in details_data.get("items", []):
            if item["status"]["embeddable"] == True:
                videos.append({"video_id": item["id"], "title": item["snippet"]["title"]})
            if len(videos) == 2:
                break

        # SERP + save to Content table
        serp_search = GoogleSearch({"q": query, "api_key": settings.SERP_API_KEY, "num": 5})
        serp_results = serp_search.get_dict()
        links = []

        for result in serp_results.get("organic_results", [])[:5]:
            title = result.get("title", "")
            url = result.get("link", "")
            snippet = result.get("snippet", "")
            source_name = result.get("source", "Web")

            # save source
            source_obj, _ = Source.objects.get_or_create(source_name=source_name)

            # save content
            Content.objects.get_or_create(
                url=url,
                defaults={
                    "title": title,
                    "snippet": snippet,
                    "source": source_obj
                }
            )

            links.append({"title": title, "url": url, "snippet": snippet})

        # save youtube videos as content too
        yt_source, _ = Source.objects.get_or_create(source_name="YouTube")
        for video in videos:
            Content.objects.get_or_create(
                url=f"https://www.youtube.com/watch?v={video['video_id']}",
                defaults={
                    "title": video["title"],
                    "snippet": "",
                    "source": yt_source
                }
            )

        # save everything to search record
        search.videos_json = json.dumps(videos)
        search.links_json = json.dumps(links)
        search.save()

        return JsonResponse({
            "status": "success",
            "query": query,
            "answer": answer,
            "videos": videos,
            "links": links
        })

@csrf_exempt
def history_api(request):
    if request.method == "GET":
        searches = SearchQuery.objects.filter(
            user=request.user
        ).order_by("-created_at")[:20]

        history = []
        for s in searches:
            history.append({
                "query": s.query_text,
                "answer": s.answer_text,
                "videos": json.loads(s.videos_json) if s.videos_json else [],
                "links": json.loads(s.links_json) if s.links_json else [],
                "created_at": s.created_at.strftime("%d %b %Y, %I:%M %p")
            })

        return JsonResponse({"history": history})

@csrf_exempt
def logout_user(request):
    logout(request)
    return JsonResponse({"message": "Logged out"})