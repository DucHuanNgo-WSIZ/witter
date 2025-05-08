from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Follow, Like

""" THIS IS REDUNDANT AND DEPRECATED, NO LONGER IN USE BECAUSE I REMOVED LIKE COUNT AND FOLLOW COUNT IN MODELS """

""" Function to increase follow count """
@receiver(post_save, sender=Follow)
def update_follow_count(sender, instance, created, **kwargs):
    if created:
        instance.follow_target.follower_count = instance.follow_target.followers.count()
        instance.follow_target.save()

""" Function to decrease follow count """
@receiver(post_delete, sender=Follow)
def update_like_count_on_delete(sender, instance, **kwargs):
    instance.follow_target.follower_count = instance.follow_target.followers.count()
    instance.follow_target.save()

""" Function to increase like count of a post """
@receiver(post_save, sender=Like)
def update_like_count(sender, instance, created, **kwargs):
    if created:
        instance.post.like_count = instance.post.likes.count()
        instance.post.save()

""" Function to decrease like count of a post """
@receiver(post_delete, sender=Like)
def update_like_count_on_delete(sender, instance, **kwargs):
    instance.post.like_count = instance.post.likes.count()
    instance.post.save()