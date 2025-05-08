import json
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Post, Like, Follow


def index(request):
    # Get list of all posts
    post_list = Post.objects.all().order_by("-time_created")

    # 10 posts per page
    paginator = Paginator(post_list, 10)

    # Get page number, if there isn't one, page number is 1 by default
    page_number = int(request.GET.get('page', 1))

    page_obj = paginator.get_page(page_number)

    # Render the page differently with is_liking status depending on if the user is authenticated
    if request.user.is_authenticated:
        # Make a dict to check if the user is liking each post in the page obj
        is_liking = dict()

        # Loop through all likes in page_obj to see which one the user liked
        for post in page_obj:
            is_liking[post.id] = request.user.liked_posts.all().filter(post=post).exists() # Turns out this returns a list of Likes originally.

        for post in page_obj:
            post.is_liking = is_liking.get(post.id, False) # Apparently in Django python, you can dynamically add attributes

    return render(request, "network/index.html", {
        "page_obj": page_obj
    })
    

""" Function to display posts from people the user follows """
@login_required
def following(request):
    # Get list of all profiles that user follows
    # First, we have to get a list of Follow objects
    following_objs = Follow.objects.filter(follower=request.user)    

    following_users = list() # Gradually add to this list

    for follow in following_objs:
        following_users.append(follow.follow_target) # Add each user into the list

    # Next, get a list of all posts from those users
    all_posts = Post.objects.filter(poster__in=following_users).order_by("-time_created")

    # Paginator
    paginator = Paginator(all_posts, 10)

    page_number = int(request.GET.get('page', 1))

    page_obj = paginator.get_page(page_number)

    # Make a dict to check if the user is liking each post in the page obj
    is_liking = dict()

    # Loop through all likes in page_obj to see which one the user liked
    for post in page_obj:
        is_liking[post.id] = request.user.liked_posts.all().filter(post=post).exists()

    for post in page_obj:
        post.is_liking = is_liking.get(post.id, False)

    return render(request, "network/following.html", {
        "page_obj": page_obj
    })



""" Function API to get and change post content and like count """
def post_actions(request, id: int):
    # Get post
    post = get_object_or_404(Post, id=id)

    # When info is fetched to update page
    if request.method == "GET":
        return JsonResponse(post.serialize())
    
    # Modifying post
    elif request.method == "PUT":
        # First, check for user authentication
        if not request.user.is_authenticated:
            return HttpResponse("You are not logged in", status=400)
        
        # Process information
        data = json.loads(request.body)
        if data.get("content") is not None: # Edit
            # Make sure only the owner of the post can edit it
            if request.user != post.poster:
                return HttpResponse("You are not the owner of the post", status=400)
            
            post.content = data["content"]

        if data.get("like_status") is not None: # Like
            # Check whether user wants to like or unlike post
            like_status = data["like_status"]

            # If user wants to like post
            if like_status:
                # Check if there's a duplicating like object
                if Like.objects.filter(liker=request.user, post=post):
                    return HttpResponse("Already liked post", status=400)
                
                # Create a new like object
                like_obj = Like.objects.create(liker=request.user, post=post)
                like_obj.save()

            # If user wants to unlike post
            else:
                # Check if the user already unliked post
                if not Like.objects.filter(liker=request.user, post=post):
                    return HttpResponse("Did not like post at the first place", status=400)
                
                # Get the like object to delete
                unlike_obj = get_object_or_404(Like, liker=request.user, post=post)
                unlike_obj.delete()
                
                
        post.save()
        return HttpResponse(status=204)
        

    else:
        return HttpResponse("Invalid method", status=403)


""" Function to handle creation of new posts """
@login_required
def new_post(request):
    if request.method == "GET":
        return render(request, "network/new_post.html")
    
    # Handles post submissions
    else:
        # Get content
        content = request.POST.get("content")

        # Make sure content isn't empty
        if not content:
            return HttpResponseServerError("Content is empty", 403)
        
        # Make a post object to save the new post
        post = Post(poster=request.user, content=content)

        post.save()

        return HttpResponseRedirect(reverse("index"))
        

""" Function to handle user profile page, acts as both normal page and API route """
def profile(request, id: int):
    # Get user profile
    profile = get_object_or_404(User, id=id)

    if request.method == "GET":

        # Get all posts that belong to the user
        posts = Post.objects.filter(poster=profile).order_by("-time_created")

        # 10 posts per page
        paginator = Paginator(posts, 10)

        # Get page number, if there isn't one, page number is 1 by default
        page_number = int(request.GET.get('page', 1))

        page_obj = paginator.get_page(page_number)

        # Render different things depending on whether the user is logged in or not
        if request.user.is_authenticated:
            # A boolean variable to check whether user is following this profile initially
            is_following = profile.followers.filter(follower=request.user).exists()

            # Make a dict to check if the user is liking each post in the page obj
            is_liking = dict()

            # Similar code with index function
            for post in page_obj:
                is_liking[post.id] = request.user.liked_posts.all().filter(post=post).exists()

            for post in page_obj:
                post.is_liking = is_liking.get(post.id, False)


            return render(request, "network/profile.html", {
                "profile": profile, "page_obj": page_obj, "is_following": is_following
            })
        else:
            return render(request, "network/profile.html", {
                "profile": profile, "page_obj": page_obj, "is_following": None
            })

        
    
    # PUT request, meaning user wants to follow/unfollow
    elif request.method == "PUT":
        data = json.loads(request.body)

        # Make sure only users who are logged in can follow/unfollow
        if not request.user.is_authenticated:
            return HttpResponse("You are not logged in!", status=400)
        
        # Check for data validity
        if data.get("follow") is not None:
            # Boolean to check if user wants to follow or unfollow
            to_follow = data["follow"]

            # If user wants to follow
            if to_follow:
                # As a failsafe, check whether there's an existing follow object
                follow_obj = Follow.objects.filter(follower=request.user, follow_target=profile).first()

                # If there is already a follow object, do nothing. Otherwise, make a new follow object
                if not follow_obj:
                    new_follow_obj = Follow.objects.create(follower=request.user, follow_target=profile)

                    # Check validity of new follow object
                    if not new_follow_obj.is_valid():
                        return HttpResponse("Invalid follow", status=400)
                    
                    new_follow_obj.save()

            # If user wants to unfollow
            else:
                # Get the existing follow object
                follow_obj = Follow.objects.filter(follower=request.user, follow_target=profile).first()

                # If there is already no follow objects, do nothing. Otherwise, remove the follow object
                if follow_obj:
                    follow_obj.delete()
        else:
            return HttpResponse(status=400)
        return HttpResponse(status=204)

    # After the PUT request, this API method will return the profile's current info to update with JS
    elif request.method == "POST":
        return JsonResponse(profile.serialize())
    
    else:
        return HttpResponseServerError("Invalid method", 403)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
