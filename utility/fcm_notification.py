
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
