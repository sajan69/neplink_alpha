# accounts/tasks.py
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from push_notifications.models import GCMDevice
from firebase_admin import messaging
import logging
from .models import Notification, User

logger = logging.getLogger(__name__)

@shared_task
def send_notification(title, body, user_ids, link):
    logger.info(f"Starting send_notification task for users: {user_ids}")
    
    # Store notifications in the database
    store_notifications(title, body, user_ids, link)
    
    # Send push notifications
    send_push_notifications(title, body, user_ids, link)

    logger.info("Notification task completed")

def store_notifications(title, body, user_ids, link):
    try:
        for user_id in user_ids:
            Notification.objects.create(
                user_id=user_id,
                title=title,
                body=body,
                link=link,
            )
        logger.info("Created notification objects")
    except Exception as e:
        logger.error(f"Error creating notification objects: {str(e)}")

def send_push_notifications(title, body, user_ids, link):
    try:
        devices = GCMDevice.objects.filter(user__id__in=user_ids)
        logger.info(f"Found {devices.count()} devices")
        
        for device in devices:
            try:
                logger.info(f"Sending message to device {device.id}")
                device.send_message(title, body=body, extra={"link": link})
                logger.info(f"Successfully sent message to device {device.id}")
            except Exception as e:
                logger.error(f"Error sending message to device {device.id}: {str(e)}")
    except Exception as e:
        logger.error(f"Error in send_push_notifications: {str(e)}")