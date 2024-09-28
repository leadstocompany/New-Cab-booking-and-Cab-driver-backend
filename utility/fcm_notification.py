# import requests

# def send_fcm_notification(fcm_token, title, body, data):
#     # FCM endpoint
#     url = "https://fcm.googleapis.com/fcm/send"

#     # FCM Server key (replace with your actual key)
#     server_key = 'server_key'

#     # Headers
#     headers = {
#         'Authorization': f'key={server_key}',
#         'Content-Type': 'application/json',
#     }

#     # Payload
#     payload = {
#         "to": fcm_token,  # FCM token of the customer
#         "notification": {
#             "title": title,  # Title of the notification
#             "body": body,    # Body of the notification
#         },
#         "data": data
#     }

#     # Send the POST request
#     response = requests.post(url, headers=headers, json=payload)

#     # Check response
#     if response.status_code == 200:
#         return f"FCM notification sent successfully!"
#     else:
#         return response.content
        
# pip install firebase-admin
# 

import firebase_admin
from firebase_admin import credentials, messaging

# Path to your service account key JSON file
cred = credentials.Certificate('jomlah-cab-app-firebase-adminsdk-6alay-32a4d2af4c.json')

# Initialize the Firebase app with the service account credentials
firebase_admin.initialize_app(cred)

# Function to send a notification
def send_push_notification(fcm_token, title, body,data):
    # Create a message
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data,
        token=fcm_token,  # Token of the device you want to send the message to
    )

    # Send the message
    response = messaging.send(message)
    print('Successfully sent message:', response)
