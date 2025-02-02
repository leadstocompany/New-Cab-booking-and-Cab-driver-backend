from firebase_admin import messaging
import os


# Function to send a notification
def send_fcm_notification(fcm_token, title, body):

    # Create a message
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=fcm_token,  # Token of the device you want to send the message to
    )

    # Send the message
    response = messaging.send(message)
    # print('Successfully sent message:', response)
    return response


def send_rich_fcm_notification(
    fcm_token, title, message, banner=None, url=None, type="admin_notification"
):
    """Send FCM notification with banner image and URL redirection"""

    notification = messaging.Notification(title=title, body=message, image=banner)

    data = {
        "click_action": "FLUTTER_NOTIFICATION_CLICK",
        "url": url if url else "",
        "type": type,
    }

    message = messaging.Message(notification=notification, data=data, token=fcm_token)

    return messaging.send(message)
