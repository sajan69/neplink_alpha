# post/tasks.py
from celery import shared_task
from accounts.models import User
from accounts.services import NotificationService

@shared_task(bind=True, max_retries=3)
def send_post_notification(self, action, user_id, target_user_id, post_id, content=None):
    try:
        NotificationService.send_post_notification(action, user_id, target_user_id, post_id, content)
        username = User.objects.get(id=target_user_id).username
        print(f"Notification sent successfully for action {action} to {username}")
    except Exception as e:
        print(f"Error in send_post_notification: {str(e)}")
        if self.request.retries < self.max_retries:
            self.retry(exc=e, countdown=2 ** self.request.retries)
        else:
            print(f"Max retries reached for send_post_notification task. Action: {action}, User: {user_id}, Target: {target_user_id}, Post: {post_id}")
            # You might want to log this error or handle it in some way