from itertools import chain
from  django . shortcuts  import  get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from . models import  Followers, LikePost, Post, Profile
from django.db.models import Q



def signup(request):
    try:
        # Check if the request method is POST (the user has submitted the signup form)
        if request.method == 'POST':  
            username = request.POST.get('username')  
            email = request.POST.get('email') 
            password = request.POST.get('password')  
            print(username, email, password)  # Print the retrieved data (for debugging purposes)

            # Create a new user and save it to the database
            new_user = User.objects.create_user(username, email, password)
            new_user.save() 

            # Retrieve the newly created user model by username 
            user_model = User.objects.get(username=username)

            # Create a new profile for the newly created user and save it to the database
            new_profile = Profile.objects.create(user=user_model)
            new_profile.save()  

            # If the user was created successfully, log them in, and redirect to the home page
            if new_user is not None:
                login(request, new_user) 
                return redirect('/') 
            
            return redirect('/loginn')  # Redirect to the login page if user creation failed
    
    # Handle any exceptions
    except Exception as e:
        print(e)  # Print the exception for debugging purposes
        error_message = "User already exists or another error occurred"    
        return render(request, 'signup.html', {'error_message': error_message})  # Render the signup page with the error message
    
    return render(request, 'signup.html')  # Render the signup page if the request method is not POST


def loginn(request):
 
  # Check if the request method is POST 
  if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username,password)

        # Authenticate the user with the provided username and password
        authenticated_user = authenticate(request, username=username, password=password)

        # Check if the authentication was successful, log thrm in and redirect to the home page
        if authenticated_user is not None:
            login(request, authenticated_user)
            return redirect('/')
        
         # If authentication failed, set an error message
        error_message ="Invalid Credentials"
        return render(request, 'loginn.html',{'error_message':error_message})

   # Render the login page if the request method is not POST
  return render(request, 'loginn.html')

#This decorator ensures that only authenticated users can access this view. 
#If an unauthenticated user tries to access it, they are redirected to the URL specified in login_url
@login_required(login_url='/loginn')
def logoutt(request):
    logout(request)
    return redirect('/loginn')



@login_required(login_url='/loginn')
def home(request):
    
    # Retrieve users followed by the current user
    following_users = Followers.objects.filter(follower=request.user.username).values_list('user', flat=True)

    # Retrieve posts belonging to the user and their followers.
    post = Post.objects.filter(Q(user=request.user.username) | Q(user__in=following_users)).order_by('-created_at')

    # Retrieve the profile of the current user
    profile = Profile.objects.get(user=request.user)

    context = {
        'post': post,
        'profile': profile,
    }

    # Render the home page with posts and profile data
    return render(request, 'main.html',context)
    

# View function for handling post uploads
@login_required(login_url='/loginn')
def upload(request):
    # Check if the request method is POST
    if request.method == 'POST':
        # Extract username, image, and caption from the request
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        # Create a new Post instance and save it to the database
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        # Redirect to the home page after successful upload
        return redirect('/')
    else:
        # Redirect to the home page if the request method is not POST
        return redirect('/')


# View function for handling likes/unlikes on posts
@login_required(login_url='/loginn')
def likes(request, id):
    if request.method == 'GET':
        # Extract username and post object from the request
        username = request.user.username
        post = get_object_or_404(Post, id=id)

        # Check if the user has already liked the post
        like_filter = LikePost.objects.filter(post_id=id, username=username).first()

        # If the user hasn't liked the post, create a new like; otherwise, delete the existing like
        if like_filter is None:
            new_like = LikePost.objects.create(post_id=id, username=username)
            post.no_of_likes = post.no_of_likes + 1
        else:
            like_filter.delete()
            post.no_of_likes = post.no_of_likes - 1

        post.save()

        # Redirect to the post's detail page after processing the like/unlike action
        return redirect('/#'+id)

    
# View function for rendering the explore page
@login_required(login_url='/loginn')
def explore(request):
    # Retrieve all posts and the user's profile, ordered by creation date
    post=Post.objects.all().order_by('-created_at')
    profile = Profile.objects.get(user=request.user)

    # Prepare the context dictionary for rendering the explore page
    context={
        'post':post,
        'profile':profile
        
    }
    # Render the explore page with the context data
    return render(request, 'explore.html',context)

    
# View function for rendering the user's profile page
@login_required(login_url='/loginn')
def profile(request, profile_id):
    # Retrieve the user object corresponding to the given username
    user_object = User.objects.get(username=profile_id)
    
    # Retrieve the profile objects for the logged-in user and the user whose profile is being viewed
    profile = Profile.objects.get(user=request.user)
    user_profile = Profile.objects.get(user=user_object)
    
    # Retrieve the posts made by the user whose profile is being viewed
    user_posts = Post.objects.filter(user=profile_id).order_by('-created_at')
    
    # Calculate the number of user posts
    user_post_length = len(user_posts)

    # Determine if the logged-in user follows the user whose profile is being viewed
    follower = request.user.username
    user = profile_id
    
    if Followers.objects.filter(follower=follower, user=user).first():
        follow_unfollow = 'Unfollow'
    else:
        follow_unfollow = 'Follow'

    # Calculate the number of followers and following for the user whose profile is being viewed
    user_followers = len(Followers.objects.filter(user=profile_id))
    user_following = len(Followers.objects.filter(follower=profile_id))

    # Prepare the context dictionary for rendering the user's profile page
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'profile': profile,
        'follow_unfollow': follow_unfollow,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    
    # Update user profile information if the logged-in user is viewing their own profile
    if request.user.username == profile_id:
        if request.method == 'POST':
            if request.FILES.get('image') == None:
                image = user_profile.profile_image
                bio = request.POST['bio']
                location = request.POST['location']

                user_profile.profile_image = image
                user_profile.bio = bio
                user_profile.location = location
                user_profile.save()
            if request.FILES.get('image') != None:
                image = request.FILES.get('image')
                bio = request.POST['bio']
                location = request.POST['location']

                user_profile.profile_image = image
                user_profile.bio = bio
                user_profile.location = location
                user_profile.save()

            return redirect('/profile/'+profile_id)
        else:
            return render(request, 'profile.html', context)
    return render(request, 'profile.html', context)

# View function for deleting a post
@login_required(login_url='/loginn')
def delete(request, id):
    # Retrieve the post object to be deleted
    post = Post.objects.get(id=id)
    
    # Delete the post object
    post.delete()

    # Redirect to the user's profile page after successful deletion
    return redirect('/profile/'+ request.user.username)

# View function for handling search queries
@login_required(login_url='/loginn')
def search_results(request):
    # Extract the search query from the request
    query = request.GET.get('q')

    # Retrieve users and posts matching the search query
    users = Profile.objects.filter(user__username__icontains=query)
    posts = Post.objects.filter(caption__icontains=query)

    # Prepare the context dictionary for rendering the search results page
    context = {
        'query': query,
        'users': users,
        'posts': posts,
    }

    # Render the search results page with the context data
    return render(request, 'search_user.html', context)

# View function for rendering a specific post on the home page
def home_post(request,id):
    # Retrieve the post object corresponding to the given id
    post = Post.objects.get(id=id)
    
    # Retrieve the profile object for the logged-in user
    profile = Profile.objects.get(user=request.user)
    
    # Prepare the context dictionary for rendering the post on the home page
    context={
        'post':post,
        'profile':profile
    }
    
    # Render the home page with the context data
    return render(request, 'main.html', context)



# View function for handling follow/unfollow actions
def follow(request):
    # Check if the request method is POST
    if request.method == 'POST':
        # Extract the follower and user from the request
        follower = request.POST['follower']
        user = request.POST['user']

        # Check if a follow relationship already exists between the follower and user
        if Followers.objects.filter(follower=follower, user=user).first():
            # If a follow relationship exists, delete the relationship (unfollow)
            delete_follower = Followers.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            # If no follow relationship exists, create a new relationship (follow)
            new_follower = Followers.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        # Redirect to the home page if the request method is not POST
        return redirect('/')
