from django.test import TestCase, Client
from .models import Post, User, Follow, Like

# Create your tests here.

""" When there are over 10 posts in all posts """
class AllPosts_Over10(TestCase):

    def setUp(self):
        # Get a user
        user = User.objects.create()
        # Create multiple posts
        for i in range(15):
            Post.objects.create(content=f"Post {i}", poster=user)

    def test_pagination(self):
        client = Client()
        response = client.get('')
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_pagination2(self):
        client = Client()
        response = client.get('?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)    


""" When there are less than 10 posts in all posts """
class AllPosts_Under10(TestCase):
    def setUp(self):
        # Make a user
        user = User.objects.create()

        # Create some posts
        for i in range(5):
            Post.objects.create(poster=user, content=f"Post {i}")

    def test_pagination(self):
        client = Client()
        response = client.get('')
        self.assertEqual(len(response.context['page_obj']), 5)


""" Check for follow validity """
class FollowValidity(TestCase):
    def setUp(self):
        # Make some users
        user = User.objects.create(id=1, username="foo")
        user2 = User.objects.create(id=2, username="bar")

        # Make some follows
        follow = Follow.objects.create(follower=user, follow_target=user2)
        follow2 = Follow.objects.create(follower=user2, follow_target=user)
        follow_invalid = Follow.objects.create(follower=user, follow_target=user)

    def test_followValidity(self):
        # Get the users back
        user = User.objects.get(id=1)
        user2 = User.objects.get(id=2)

        # Get the follows back
        follow = Follow.objects.get(follower=user, follow_target=user2)
        follow2 = Follow.objects.get(follower=user2, follow_target=user)
        follow_invalid = Follow.objects.get(follower=user, follow_target=user)

        self.assertTrue(follow.is_valid())
        self.assertTrue(follow2.is_valid())
        self.assertFalse(follow_invalid.is_valid())


""" Check for like count validity """
class LikeCountValidity(TestCase):
    def setUp(self):
        # Make a lot of users
        user = User.objects.create(id=1, username="foo")
        user2 = User.objects.create(id=2, username="bar")
        user3 = User.objects.create(id=3, username="baz")
        user4 = User.objects.create(id=4, username="Harry")

        # Make a post
        post = Post.objects.create(poster=user4, content="Harry Potter")

        # Make some like objects
        like1 = Like.objects.create(liker=user, post=post)
        like2 = Like.objects.create(liker=user2, post=post)
        like3 = Like.objects.create(liker=user3, post=post)

    def test_likeCount(self):
        # Get the post
        post = Post.objects.all().first()

        self.assertEqual(Like.objects.filter(post=post).count(), 3)    
