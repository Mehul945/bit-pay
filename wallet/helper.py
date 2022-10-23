from trycourier import Courier
client = Courier(auth_token="pk_test_DDKR2Q0F8C4VM5JYPDDPXRRWCCXW")
def send_transaction_email(status,email,username,amount,bit_id):
    resp = client.send_message(
                message={
                    "to": {
                    "email": f"{email}"
                    },
                    "template": "0QG3HBMKB7MXKCKDWKXAF8THNZAC",
                    "data": {
                        "recipientName": f"{username}",
                        "user1":f"{bit_id}",
                        "amount":f"{amount*0.00000001:.8f} BTC",
                        "status":f"{status}",
                    },
                }
            )

def send_verification_link(email,username,token):
    resp = client.send_message(
        message={
            "to": {
            "email": f"{email}",
            },
            "template": "8FNSMHKQD7MC7TP6QSN494619NEQ",
            "data": {
            "username": f"{username}",
            "link": f"https://8000-cs-513293748685-default.cs-asia-southeast1-yelo.cloudshell.dev/verify/{token}",
            },
        }
        )

