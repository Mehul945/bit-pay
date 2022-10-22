from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Details,address_book
from bitcoinlib.wallets import wallet_create_or_open,wallet_delete
from bitcoinlib.mnemonic import Mnemonic
import pickle
from functools import lru_cache
from trycourier import Courier
client = Courier(auth_token="pk_test_DDKR2Q0F8C4VM5JYPDDPXRRWCCXW")


wallet=None
def index(request):
    if request.user.is_authenticated:
        detail=Details.objects.filter(private_key=request.user.last_name).values()
        return render(request, 'index.htm',{"detail":detail.get()})
    return render(request, 'index.htm')

def login(request):
    global wallet
    if request.user.is_authenticated:
        refresh(request)
        return redirect("/")
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            refresh(request)
            auth.login(request, user)
            detail=Details.objects.filter(private_key=request.user.last_name).values()
            wallet=wallet_create_or_open(keys=detail[0]['phrase'],name=request.user.username,network='testnet',witness_type="segwit")
            return redirect("/")
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('login')
    
    return render(request, 'login.htm')

def register(request):
    if request.method != 'POST':
        return render(request, 'register.htm')
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    password2 = request.POST['password2']
    
    if password!=password2:
        messages.info(request, 'password didn"t match')
        return  redirect('register')

    if User.objects.filter(email=email).exists():
        messages.info(request, 'Email Taken')
        return redirect('register')

    elif User.objects.filter(username=username).exists():
        messages.info(request, 'Username Taken')
        return redirect('register')
    else:
        phrase=Mnemonic().generate()
        pickle.dump(file=open(username+'.pkl',"wb"),obj=phrase)
        detail=Details()
        wallet=wallet_create_or_open(keys=phrase,name=username,network='testnet',witness_type="segwit")
        key=wallet.get_key()
        detail.balance=wallet.balance()
        detail.balance1=wallet.balance()
        detail.phrase=phrase
        detail.address=key.address
        detail.private_key=key.wif
        user = User.objects.create_user(username=username, email=email, password=password, last_name=key.wif, first_name=key.address)
        user.save()
        detail.save()
        print('User Created')
        return redirect('login')

    return redirect('/')

def logout(request):
    auth.logout(request)
    return redirect('/')

@lru_cache
def refresh(request):
    global wallet
    if wallet != None and request.user.is_authenticated:
        wallet.scan()
        wallet.utxos_update()
        detail=Details.objects.filter(private_key=request.user.last_name).values()
        detail.update(balance=wallet.balance(as_string=True))


def send(request):
    global wallet
    if wallet!=None and request.method=="POST":
        amount=int(request.POST["amount"])
        bit_id=request.POST["bit_id"]
        if (amount+1000)>wallet.balance():
            messages.info(request, "No enough fund")
            return redirect("/")
        pub_key=address_book.objects.filter(bit_id=bit_id)
        if pub_key.exists():
            pub_key=pub_key.values().get()
            trx=wallet.send_to(pub_key["Address"],amount,fee=1000,network="testnet")
            trx.send(offline=False)
            status="successful"
            if not trx.pushed:
                messages.info(request, 'Transaction failed')
                status="Failed"
            resp = client.send_message(
                message={
                    "to": {
                    "email": f"{request.user.email}"
                    },
                    "template": "0QG3HBMKB7MXKCKDWKXAF8THNZAC",
                    "data": {
                        "recipientName": f"{request.user.username}",
                        "user1":f"{bit_id}",
                        "amount":f"{amount*0.00000001:.8f} BTC",
                        "status":f"{status}",
                    },
                }
            )
            print(trx.info())
        else:
            messages.info(request, 'User not found')
            
    return redirect("/")
