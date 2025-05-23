import requests
from JLP_MyRide import settings
from twilio.rest import Client
# url = "https://www.fast2sms.com/dev/bulkV2"

# def send_otp(otp:int, phone:str):
#     print(otp)
#     payload = f"variables_values={otp}&route=otp&numbers={phone}"
#     headers = {
#         'authorization': settings.FAST2SMS,
#         'Content-Type': "application/x-www-form-urlencoded",
#         'Cache-Control': "no-cache",
#         }

#     response = requests.request("POST", url, data=payload, headers=headers)

#     print(response.text)


# def send_otp(otp:int, phone:str):
#     # Send the OTP using Twilio
#     client = Client("SKa7338e3aecc0fa3ecfb402bb4ddf7b47", settings.TWILIO_AUTH_TOKEN)
#     message = client.messages.create(
#     body=f'Your OTP is {otp}',
#         from_=settings.TWILIO_PHONE_NUMBER,
#         to=phone
#     )



def send_otp(otp: int, phone: str):
    try:
        # Use the correct AccountSid and AuthToken
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Create and send the message
        message = client.messages.create(
            body=f'Your OTP Jomlah Ride is {otp}',
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone
        )
        
        return message.sid  # Return the message SID if needed

    except Exception as e:
        # Print the error message
        print(f"Failed to send OTP: {e}")
        return None




# # Download the helper library from https://www.twilio.com/docs/python/install
# import os
# from twilio.rest import Client

# # Find your Account SID and Auth Token at twilio.com/console
# # and set the environment variables. See http://twil.io/secure
# account_sid = os.environ["TWILIO_ACCOUNT_SID"]
# auth_token = os.environ["TWILIO_AUTH_TOKEN"]
# client = Client(account_sid, auth_token)

# message = client.messages.create(
#     body="Join Earth's mightiest heroes. Like Kevin Bacon.",
#     from_="+15017122661",
#     to="+15558675310",
# )

# print(message.body)