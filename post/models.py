from django.db import models
from accounts.models import User

class Post(models.Model):
    class Feeling(models.TextChoices):
        HAPPY = 'happy', 'Happy'
        SAD = 'sad', 'Sad'
        ANGRY = 'angry', 'Angry'
        SURPRISED = 'surprised', 'Surprised'
        LOVE = 'love', 'Love'
        THANKFUL = 'thankful', 'Thankful'
        CONFUSED = 'confused', 'Confused'
        EXCITED = 'excited', 'Excited'
        CALM = 'calm', 'Calm'
        NONE = 'none', 'None'

    class Visibility(models.TextChoices):
        EVERYONE = 'everyone', 'Everyone'
        FRIENDS = 'friends', 'Friends'
        PRIVATE = 'private', 'Private'
        SELECTED = 'selected', 'Selected Friends'
        
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    feeling = models.CharField(max_length=50, choices=Feeling.choices, default=Feeling.HAPPY)
    is_hidden = models.BooleanField(default=False)
    visibility = models.CharField(max_length=50, choices=Visibility.choices, default=Visibility.EVERYONE)
    shared_post = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='shares')
    is_shared = models.BooleanField(default=False)
    tagged_users = models.ManyToManyField(User, related_name='tagged_posts', blank=True)

    def __str__(self):
        return f"Post by {self.user.username} - {self.created_at}"
    
class PostMedia(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='post_media/')
    file_type = models.CharField(max_length=10, choices=[('image', 'Image'), ('video', 'Video'), ('audio', 'Audio')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_type} for post {self.post.id}"
    
class SelectedFriend(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='selected_friends')
    friend = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['post', 'friend']   

class UserTagSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tag_settings')
    allow_tagging = models.BooleanField(default=True)
    show_tagged_posts = models.BooleanField(default=True)

    def __str__(self):
        return f"Tag settings for {self.user.username}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    comment_reply = models.ForeignKey('CommentReply', on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['user', 'post'], ['user', 'comment'], ['user', 'comment_reply']]

    def __str__(self):
        if self.post:
            return f"Like by {self.user.username} on Post {self.post.id}"
        elif self.comment:
            return f"Like by {self.user.username} on Comment {self.comment.id}"
        else:
            return f"Like by {self.user.username} on CommentReply {self.comment_reply.id}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on Post {self.post.id}"

class CommentReply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reply by {self.user.username} on Comment {self.comment.id}"