from django import forms
from .models import Post, Comment, CommentReply

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['caption', 'media', 'feeling']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class CommentReplyForm(forms.ModelForm):
    class Meta:
        model = CommentReply
        fields = ['text']