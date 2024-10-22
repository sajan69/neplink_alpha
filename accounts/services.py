import threading
from push_notifications.models import GCMDevice

from firebase_admin import messaging
from google.api_core.exceptions import NotFound
from django.contrib.contenttypes.models import ContentType 
from accounts.models import Notification, User
from firebase_admin.exceptions import FirebaseError
 
class NotificationService:
    @staticmethod
    def register_device(registration_id, user=None):
        """
        Registers a device with the given registration ID. Optionally associates the device with a user.

        Parameters:
        -----------
        registration_id : str
            The registration ID of the device.
        user : User, optional
            The user to associate with the device (default is None).

        Returns:
        --------
        dict
            A dictionary indicating success or error, and whether the device was newly created.
        """
        if not registration_id:
            return {"error": "Missing registration_id"}

        device, created = GCMDevice.objects.get_or_create(registration_id=registration_id, user=user)
        device.active = True
        device.save()
        return {"success": True, "created": created}

    @staticmethod
    def check_and_register_device(registration_id, user):
        """
        Checks if a device with the given registration ID is already registered for the user. If not, registers the device.

        Parameters:
        -----------
        registration_id : str
            The registration ID of the device.
        user : User
            The user to associate with the device.
        """
        existing_device = GCMDevice.objects.filter(registration_id=registration_id, user=user).first()
        if not existing_device:
            NotificationService.register_device(registration_id, user)
        else:
            existing_device.active = True
            existing_device.save()

    def store_notification(user_id, title, body, link=None, data=None):
        Notification.objects.create(
            user_id=user_id,
            title=title,
            body=body,
            link=link,  # Store the link
            data=data or {}
        )

    @staticmethod
    def send_notification_to_all(title, body, link=None):
        """
        Sends a notification to all registered devices.

        Parameters:
        -----------
        title : str
            The title of the notification.
        body : str
            The body of the notification.

        Returns:
        --------
        list
            A list of dictionaries containing the device registration ID and the response or error for each device.
        """
        devices = GCMDevice.objects.all()

        return NotificationService._send_to_devices(devices, title, body, link)

    @staticmethod
    def send_notification_to_condition(title, body, link=None, **condition):
        """
        Sends a notification to devices that match the specified condition.

        Parameters:
        -----------
        title : str
            The title of the notification.
        body : str
            The body of the notification.
        **condition : dict
            Keyword arguments representing the filter conditions to apply to the device query.

        Returns:
        --------
        list
            A list of dictionaries containing the device registration ID and the response or error for each device.
        """
        devices = GCMDevice.objects.filter(**condition)
    
        return NotificationService._send_to_devices(devices, title, body, link)
    
    
    @staticmethod
    def _send_to_devices(devices, title, body, link=None):
        """
        Helper method to send notifications to a list of devices.

        Parameters:
        -----------
        devices : QuerySet
            A queryset of GCMDevice instances to send the notification to.
        title : str
            The title of the notification.
        body : str
            The body of the notification.
        link : str, optional
            The link to be included in the notification data.

        Returns:
        --------
        list
            A list of dictionaries containing the device registration ID and the response or error for each device.
        """
        results = []

        for device in devices:
            try:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    token=device.registration_id,
                    data={'link': link} if link else None
                )
                response = messaging.send(message)
                results.append({'device': device.registration_id, 'response': response})
            except FirebaseError as e:
                error_code = e.code if hasattr(e, 'code') else 'unknown'
                if error_code == 'registration-token-not-registered':
                    NotificationService.remove_invalid_device(device.registration_id)
                    results.append({'device': device.registration_id, 'error': 'Token unregistered and removed'})
                elif error_code == 'invalid-argument':
                    results.append({'device': device.registration_id, 'error': 'Invalid token'})
                elif "Requested entity was not found" in str(e):
                    print(f"Token not found, removing: {device.registration_id}")
                    NotificationService.remove_invalid_device(device.registration_id)
                    results.append({'device': device.registration_id, 'error': 'Token not found and removed'})
                else:
                    print(f"Error sending notification in firebase: {str(e)}")
                    results.append({'device': device.registration_id, 'error': str(e)})
            except Exception as e:
                print(f"Error sending notification without firebase error: {str(e)}")
                results.append({'device': device.registration_id, 'error': str(e)})

        print(results)
        return results 

    @staticmethod
    def remove_invalid_device(registration_id):
        """
        Removes an invalid device from the database.

        Parameters:
        -----------
        registration_id : str
            The registration ID of the device to be removed.
        """
        GCMDevice.objects.filter(registration_id=registration_id).delete()
        print(f"Removed invalid device with registration_id: {registration_id}")


    @staticmethod
    def update_device_token(old_token, new_token, user=None):
        """
        Updates the device token in the database.

        Parameters:
        -----------
        old_token : str
            The old registration ID of the device.
        new_token : str
            The new registration ID of the device.
        user : User, optional
            The user associated with the device (default is None).

        Returns:
        --------
        dict
            A dictionary indicating success or error.
        """
        try:
            device = GCMDevice.objects.get(registration_id=old_token)
            device.registration_id = new_token
            device.save()
            return {"success": True, "message": "Device token updated successfully"}
        except GCMDevice.DoesNotExist:
            return NotificationService.register_device(new_token, user)
        except Exception as e:
            return {"error": str(e)}
  
    @staticmethod
    def send_notification_to_userids(title, body, userids, link=None):
        """
        Sends a notification to devices that match the specified userids.

        Parameters:
        -----------
        title : str
            The title of the notification.
        body : str
            The body of the notification.
        userids : list
            A list of userids to send the notification to.

        Returns:
        --------
        list
            A list of dictionaries containing the device registration ID and the response or error for each device.
        """
        devices = GCMDevice.objects.filter(user__id__in=userids)
        results = NotificationService._send_to_devices(devices, title, body, link)

        #Store notification in Firestore for each user
        for userid in userids:
            NotificationService.store_notification(userid, title, body, link)
        return results
    
  
    @staticmethod
    def send_notification_to_userids_admin(title, body, userids, link=None):
        """
        Sends a notification to devices that match the specified userids.

        Parameters:
        -----------
        title : str
            The title of the notification.
        body : str
            The body of the notification.
        userids : list
            A list of userids to send the notification to.

        Returns:
        --------
        list
            A list of dictionaries containing the device registration ID and the response or error for each device.
        """
        devices = GCMDevice.objects.filter(user__id__in=userids)
        results = NotificationService._send_to_devices(devices, title, body, link)

        
        return results
    
    

    @staticmethod
    def send_notification_async(action, user_id, target_user_id, post_or_room_id, content=None):
        def send_notification_thread():
            try:
                if action in ['like_post', 'like_comment', 'add_comment', 'share_post', 'like_reply', 'add_reply', 'tag_friend']:
                    NotificationService.send_post_notification(action, user_id, target_user_id, post_or_room_id, content)
                elif action in ['send_friend_request', 'accept_friend_request']:
                    NotificationService.send_friend_notification(action, user_id, target_user_id)
                elif action in ['new_message']:
                    NotificationService.send_message_notification(user_id, target_user_id, post_or_room_id, content)
                else:
                    print(f"Unknown action: {action}")
            except Exception as e:
                print(f"Error sending notification: {str(e)}")

        thread = threading.Thread(target=send_notification_thread)
        thread.start()

    @staticmethod
    def send_message_notification(user_id, target_user_id, room_id, content):
        sender = User.objects.get(id=user_id)
        title = f"New message from {sender.username}"
        body = content if content else "You have a new message"
        link = f"/chat/{room_id}/"
        
        devices = GCMDevice.objects.filter(user__id=target_user_id)
        
        NotificationService._send_to_devices(devices, title, body, link)

        # Store notification in database
        NotificationService.store_notification(target_user_id, title, body, link)

    @staticmethod
    def send_friend_notification(action, user_id, target_user_id):
        username = User.objects.get(id=user_id).username
        actions = {
            'send_friend_request': (f"New Friend Request", f"{username} sent you a friend request"),
            'accept_friend_request': (f"Friend Request Accepted", f"{username} accepted your friend request"),
        }

        if action in actions:
            title, body = actions[action]
            link = '/friends/requests/' if action == 'send_friend_request' else '/friends/'
            devices = GCMDevice.objects.filter(user__id=target_user_id)
            
            NotificationService._send_to_devices(devices, title, body, link)

            # Store notification in database
            NotificationService.store_notification(target_user_id, title, body, link)

    @staticmethod
    def send_post_notification(action, user_id, target_user_id, post_id, content=None):
        username = User.objects.get(id=user_id).username
        actions = {
            'like_post': (f"{username} liked your post", f"{username} liked your post"),
            'like_comment': (f"{username} liked your comment", f"{username} liked your comment" + (f": {content[:50]}..." if content else "")),
            'add_comment': (f"{username} commented on your post", f"{username} commented" + (f": {content[:50]}..." if content else "")),
            'share_post': (f"{username} shared your post", f"{username} shared your post"),
            'like_reply': (f"{username} liked your reply", f"{username} liked your reply" + (f": {content[:50]}..." if content else "")),
            'add_reply': (f"{username} replied to your comment", f"{username} replied" + (f": {content[:50]}..." if content else "")),
            'tag_friend': (f"{username} tagged you in a post", f"{username} tagged you in a post" + (f": {content[:50]}..." if content else "")),
        }

        if action in actions:
            title, body = actions[action]
            link = f"/post/{post_id}/"
            devices = GCMDevice.objects.filter(user__id=target_user_id)
            
            NotificationService._send_to_devices(devices, title, body, link)

            # Store notification in database
            NotificationService.store_notification(target_user_id, title, body, link)

    
    @staticmethod
    def get_user_notifications(user_id, limit=20, offset=0):
        return Notification.objects.filter(user_id=user_id)[offset:offset+limit]

    @staticmethod
    def mark_notification_as_read(user_id, notification_id):
        Notification.objects.filter(id=notification_id, user_id=user_id).update(read=True)

    @staticmethod
    def get_unread_notification_count(user_id):
        return Notification.objects.filter(user_id=user_id, read=False).count()

    @staticmethod
    def mark_all_notifications_as_read(user_id):
        Notification.objects.filter(user_id=user_id, read=False).update(read=True)

    @staticmethod
    def delete_old_notifications(days=30):
        from django.utils import timezone
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        Notification.objects.filter(timestamp__lt=cutoff_date).delete()
