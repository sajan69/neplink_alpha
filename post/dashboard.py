from django.contrib.auth import get_user_model
from django.db.models import Count, Q, F
from django.db.models.functions import TruncDate
from post.models import Post, Comment, Like
import json

User = get_user_model()

def admin_dashboard(request):
    # Only process for staff members
    if not request.user.is_staff:
        return {}

    context = {}
    
    # Basic statistics
    context['total_users'] = User.objects.count()
    context['total_posts'] = Post.objects.count()
    context['total_likes'] = Like.objects.count()
    context['total_comments'] = Comment.objects.count()
    context['total_shares'] = Post.objects.filter(is_shared=True).count()

    # User growth data
    user_growth = User.objects.annotate(date=TruncDate('date_joined')).values('date').annotate(count=Count('id')).order_by('date')
    context['user_growth_labels'] = json.dumps([entry['date'].strftime('%Y-%m-%d') for entry in user_growth])
    context['user_growth_data'] = json.dumps([entry['count'] for entry in user_growth])

    # Post activity data
    post_activity = Post.objects.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
    context['post_activity_labels'] = json.dumps([entry['date'].strftime('%Y-%m-%d') for entry in post_activity])
    context['post_activity_data'] = json.dumps([entry['count'] for entry in post_activity])

    # User activity distribution
    user_activity = User.objects.annotate(
        activity_score=Count('posts') + Count('comment') + Count('like')
    ).aggregate(
        very_active=Count('id', filter=Q(activity_score__gt=100)),
        active=Count('id', filter=Q(activity_score__range=(51, 100))),
        moderate=Count('id', filter=Q(activity_score__range=(21, 50))),
        low=Count('id', filter=Q(activity_score__range=(1, 20))),
        inactive=Count('id', filter=Q(activity_score=0))
    )
    context['user_activity_distribution'] = json.dumps([
        user_activity['very_active'],
        user_activity['active'],
        user_activity['moderate'],
        user_activity['low'],
        user_activity['inactive']
    ])

    # Most active users
    context['most_active_users'] = User.objects.annotate(
        activity_score=Count('posts') + Count('comment') + Count('like')
    ).order_by('-activity_score')[:10]

    # Most popular posts
    context['popular_posts'] = Post.objects.annotate(
        engagement_score=Count('likes') + Count('comments') * 2 + F('shares') * 3
    ).order_by('-engagement_score')[:5]

    return context