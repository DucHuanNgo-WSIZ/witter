from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass

    # Just so we can pass in JsonResponse. There isn't an already defined serialize function.
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "follower_count": self.followers.count()
        }


class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    time_created = models.DateTimeField(default=timezone.now)

    def serialize(self):
        return {
            "id": self.id,
            "content": self.content,
            "like_count": self.likes.count()
        }


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    follow_target = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")

    # Just to check validity of follow creation
    def is_valid(self):
        return self.follower != self.follow_target
    

class Like(models.Model):
    liker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liked_posts")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
