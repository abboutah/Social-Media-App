
from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime
from django.utils import timezone

#Gets the currently active user model
User = get_user_model()

# Create your models here.
class Profile(models.Model):
    # Many-to-one relationship linking each profile to a user in the User model
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Auto-incrementing primary key for the Profile model
    profile_id = models.AutoField(primary_key=True)
    # Text field for user biography, optional with a default value
    bio = models.TextField(blank=True, default='')
   # Image field for profile images, with an upload directory and default image
    profile_image = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')
    # Char field for user location, optional with a default value
    location = models.CharField(max_length=100, blank=True, default='')

    #string representation
    def __str__(self):
        return self.user.username


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    # Define a CharField representing the username of the user who created the post
    user = models.CharField(max_length=100)
    # Define an ImageField for uploading images for posts, with the upload directory specified
    image = models.ImageField(upload_to='post_images')
    # Define a TextField allowing users to provide captions for posts
    caption = models.TextField(blank=True, default='')
    # Define a DateTimeField representing the creation date and time of the post, with the default value set to the current date and time
    created_at = models.DateTimeField(default=timezone.now)
    # Define an IntegerField representing the number of likes for the post, with a default value of 0
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user


class LikePost(models.Model):
    # Define a ForeignKey field for storing the unique identifier of the liked post
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='likes')
    # Define a field for storing the username of the user who liked the post
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username

class Followers(models.Model):
    # Define a field for storing the username of the follower
    follower = models.CharField(max_length=100)
    # Define a field for storing the username of the user being followed
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user


    
    
