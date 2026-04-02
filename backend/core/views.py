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
from .models import SearchQuery, Source, Content, Topic, Category, Feedback
from .models import SearchQuery, Source, Content, Topic, Category, Feedback, Bookmark

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
    # DEBUG - Check if key is loading
    print("=== DEBUG API KEY ===")
    groq_key = settings.GROQ_API_KEY
    if groq_key:
        print(f"Key loaded: {groq_key[:15]}... (length: {len(groq_key)})")
        if groq_key.startswith("gsk_"):
            print("✅ Key format looks correct (starts with gsk_)")
        else:
            print("❌ Key format is wrong! Should start with 'gsk_'")
    else:
        print("❌ NO API KEY FOUND!")
    print("====================")
    
    # ... rest of your code
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
            "query_id": search.id,  # ADD THIS
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

@csrf_exempt
def feedback_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        query_id = data.get("query_id")
        rating = data.get("rating")  # 1 for thumbs up, -1 for thumbs down

        try:
            search = SearchQuery.objects.get(id=query_id, user=request.user)
            # find or create content for this search
            content_obj, _ = Content.objects.get_or_create(
                url=f"/search/{query_id}",
                defaults={"title": search.query_text, "snippet": ""}
            )
            Feedback.objects.create(
                user=request.user,
                content=content_obj,
                rating=rating,
                comment=""
            )
            return JsonResponse({"status": "success"})
        except SearchQuery.DoesNotExist:
            return JsonResponse({"error": "Not found"}, status=404)

@csrf_exempt
def bookmark_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        url = data.get("url")
        title = data.get("title")
        snippet = data.get("snippet", "")

        source_obj, _ = Source.objects.get_or_create(source_name="Bookmark")
        content_obj, _ = Content.objects.get_or_create(
            url=url,
            defaults={"title": title, "snippet": snippet, "source": source_obj}
        )
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            content=content_obj
        )
        if not created:
            bookmark.delete()
            return JsonResponse({"status": "removed"})
        return JsonResponse({"status": "saved"})

@csrf_exempt  
def get_bookmarks_api(request):
    if request.method == "GET":
        bookmarks = Bookmark.objects.filter(user=request.user).select_related("content").order_by("-created_at")
        data = []
        for b in bookmarks:
            data.append({
                "title": b.content.title,
                "url": b.content.url,
                "snippet": b.content.snippet
            })
        return JsonResponse({"bookmarks": data})

# Add these imports if not already present
from django.db.models import Count
from datetime import datetime

@login_required
def profile_api(request):
    if request.method == "GET":
        user = request.user
        total_searches = SearchQuery.objects.filter(user=user).count()
        total_bookmarks = Bookmark.objects.filter(user=user).count()
        total_feedback = Feedback.objects.filter(user=user).count()
        last_search = SearchQuery.objects.filter(user=user).order_by("-created_at").first()
        last_active = last_search.created_at.strftime("%d %b %Y, %I:%M %p") if last_search else "Never"
        
        return JsonResponse({
            "username": user.username,
            "email": user.email,
            "join_date": user.date_joined.strftime("%d %b %Y"),
            "total_searches": total_searches,
            "total_bookmarks": total_bookmarks,
            "total_feedback": total_feedback,
            "last_active": last_active
        })

@csrf_exempt
@login_required
def profile_update_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user = request.user
        
        new_username = data.get("username")
        new_email = data.get("email")
        
        if new_username and User.objects.exclude(id=user.id).filter(username=new_username).exists():
            return JsonResponse({"error": "Username already taken"}, status=400)
        
        if new_email and User.objects.exclude(id=user.id).filter(email=new_email).exists():
            return JsonResponse({"error": "Email already registered"}, status=400)
        
        if new_username:
            user.username = new_username
        if new_email:
            user.email = new_email
        
        user.save()
        return JsonResponse({"status": "success"})

@login_required
def search_history_api(request):
    if request.method == "GET":
        searches = SearchQuery.objects.filter(user=request.user).order_by("-created_at")[:50]
        data = []
        for s in searches:
            data.append({
                "id": s.id,
                "query": s.query_text,
                "created_at": s.created_at.strftime("%d %b %Y, %I:%M %p")
            })
        return JsonResponse({"searches": data})

@login_required
def feedback_all_api(request):
    if request.method == "GET":
        feedbacks = Feedback.objects.filter(user=request.user).select_related('content').order_by("-created_at")
        data = []
        for fb in feedbacks:
            # Try to find the search query associated with this feedback
            search = SearchQuery.objects.filter(
                user=request.user,
                query_text=fb.content.title
            ).first()
            
            data.append({
                "id": fb.id,
                "query": search.query_text if search else fb.content.title,
                "rating": fb.rating,
                "comment": fb.comment,
                "created_at": fb.created_at.strftime("%d %b %Y, %I:%M %p")
            })
        return JsonResponse({"feedback": data})

@csrf_exempt
@login_required
def feedback_submit_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        search_id = data.get("search_id")
        rating = data.get("rating")
        comment = data.get("comment", "")
        is_edit = data.get("is_edit", False)
        
        try:
            search = SearchQuery.objects.get(id=search_id, user=request.user)
            
            # Create or update feedback
            feedback, created = Feedback.objects.get_or_create(
                user=request.user,
                content__url__contains=str(search_id),
                defaults={
                    "content": Content.objects.get_or_create(
                        url=f"/search/{search_id}",
                        defaults={"title": search.query_text, "snippet": ""}
                    )[0],
                    "rating": rating,
                    "comment": comment
                }
            )
            
            if not created:
                feedback.rating = rating
                feedback.comment = comment
                feedback.save()
            
            return JsonResponse({"status": "success"})
        except SearchQuery.DoesNotExist:
            return JsonResponse({"error": "Search not found"}, status=404)

@login_required
def bookmarks_page(request):
    return render(request, "core/bookmarks.html", {"username": request.user.username})

@login_required
def feedback_page(request):
    return render(request, "core/feedback.html", {"username": request.user.username})

@login_required
def profile_page(request):
    return render(request, "core/profile.html", {"username": request.user.username})

@csrf_exempt
@login_required
def recommendations_api(request):
    if request.method == "GET":
        # Get user's search history
        searches = SearchQuery.objects.filter(user=request.user).order_by("-created_at")
        
        # Count frequency of queries
        query_counts = {}
        for search in searches:
            query = search.query_text
            query_counts[query] = query_counts.get(query, 0) + 1
        
        # Get top 6 most searched queries
        top_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:6]
        
        recommendations = []
        for query, count in top_queries:
            recommendations.append({"query": query, "count": count})
        
        return JsonResponse({"recommendations": recommendations})