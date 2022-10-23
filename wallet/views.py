from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Profile,address_book,wallet_details
from bitcoinlib.wallets import wallet_create_or_open,wallet_delete
from bitcoinlib.mnemonic import Mnemonic
import pickle
import six
from functools import lru_cache
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .helper import *

class TokenGenerator(PasswordResetTokenGenerator):  
    def _make_hash_value(self, user, timestamp):  
        return (  
            six.text_type(user.username) + six.text_type(timestamp) +  
            six.text_type(user.is_active)
            )  
wallet=None
def index(request):
    if request.user.is_authenticated:
        detail=wallet_details.objects.filter(private_key=request.user.last_name).values().first()
        print(detail)
        return render(request, 'index.htm',{"detail":detail})
    return render(request, 'index.htm')

def login(request):
    global wallet
    if request.user.is_authenticated:
        refresh(request)
        return redirect("/")
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None and Profile.objects.filter(user=user).first().is_verified:
            refresh(request)
            auth.login(request, user)
            detail=wallet_details.objects.filter(private_key=request.user.last_name).values()
            print(detail)
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
    print(User.objects.filter(email=email))
    if User.objects.filter(email=email).exists() and Profile.objects.filter(email=email).first().is_verified:
        messages.info(request, 'Email Taken')
        return redirect('register')
    elif User.objects.filter(username=username).exists() and Profile.objects.filter(username=username).first().is_verified:
        messages.info(request, 'Username Taken')
        return redirect('register')
    elif User.objects.filter(username=username).exists() and (not Profile.objects.filter(username=username).first().is_verified):
        user=User.objects.filter(username=username).first()
        token=TokenGenerator().make_token(user)
        send_verification_link(email,username,token)
        detail=Profile.objects.filter(user=user).first()
        detail.update(token=token)
        detail.save()
        return redirect('login')
    else:
        user = User.objects.create_user(username=username, email=email, password=password)
        token=TokenGenerator().make_token(user)
        send_verification_link(email,username,token)
        detail=Profile.objects.create(user=user,email=email,token=token)
        detail.save()
        user.save()
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
        detail=wallet_details.objects.filter(private_key=request.user.last_name).values()
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
            send_transaction_email(status,request.user.email,request.user.username,amount,bit_id)
            print(trx.info())
        else:
            messages.info(request, 'User not found')
            
    return redirect("/")

def verify(request,token):
    user=Profile.objects.filter(token=token).first().user
    profile=Profile.objects.filter(user=user).values()
    ch_token=TokenGenerator().check_token(user,token)
    print(ch_token)
    if ch_token and (not profile.first()["is_verified"]):
        phrase=Mnemonic().generate()
        pickle.dump(file=open(request.user.username+'.pkl',"wb"),obj=phrase)
        wallet=wallet_create_or_open(keys=phrase,name=user.username,network='testnet',witness_type="segwit")
        key=wallet.get_key()
        w_details=wallet_details.objects.create(balance=wallet.balance(as_string=True),INR_balance=0,private_key=key.wif,phrase=phrase,address=key.address)
        w_details.save()
        
        profile.update(is_verified=True)

        user_data=User.objects.filter(username=user.username)
        user_data.update(last_name=key.wif,first_name=key.address)
    return redirect("login")


def reset_password(request):
    pass