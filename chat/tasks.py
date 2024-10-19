import logging
from celery import shared_task
from accounts.services import NotificationService

logger = logging.getLogger(__name__)

@shared_task(name='chat.tasks.send_chat_notification')
def send_chat_notification(user_id, room_id, message_content, sender_username):
    logger.info(f"Starting send_chat_notification task for user {user_id}")
    try:
        NotificationService.send_notification_to_userids(
            title=f"{message_content}",
            body=f"{sender_username} sent you a message",
            userids=[user_id],
            link=f"/chat/{room_id}/"
        )
        logger.info(f"Notification sent successfully for user {user_id}")
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        raise  # Re-raise the exception so Celery knows the task failed