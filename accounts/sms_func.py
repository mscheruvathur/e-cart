

def send_sms(body,to_):
    import twilio
    from twilio.rest import Client
    account_sid = 'AC035703a4ab8e45c7dea0a023a600353f'
    auth_token = 'c8fae1942f1563f6fbc7e51f205c8d18'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
            body=body,
            from_='+17242466618',
            to = '+91' + to_
        )

def gen_otp():
    import math,random
    digits = '0123456789'
    OTP = ''
    for i in range(6):
        OTP += digits[math.floor(random.random()*10)]
    return OTP


