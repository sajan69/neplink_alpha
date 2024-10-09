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
        
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    caption = models.TextField(blank=True)
    media = models.FileField(upload_to='post_media/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    feeling = models.CharField(max_length=50, choices=Feeling.choices, default=Feeling.HAPPY)

    def __str__(self):
        return f"Post by {self.user.username} - {self.created_at}"

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