
from twilio.rest import Client
from decouple import config
# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = config('TWILIO_ACCOUNT_SID')
auth_token = config('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)


def verification(to):
    verification = client.verify.v2.services(
        "VA107715325760a6a7b2518994fe1cfe25"
    ).verifications.create(
        to=to, 
        channel="sms", 
        locale="pt"  # Configurando o idioma para português
    )

    print(verification.sid)

def send_sms():
    message = client.messages.create(
        body="Revenge of the Sith was clearly the best of the prequel trilogy.",
        messaging_service_sid="MG9752274e9e519418a7406176694466fa",
        to="+258873686545",
    )

    print(message.body)