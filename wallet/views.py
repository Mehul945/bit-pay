from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from .models import User
from django.contrib import messages
from .models import address_book,wallet_details
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
        detail=wallet_details.objects.get(private_key=request.user.last_name)
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
        if (user is not None) and User.objects.get(username=username).is_verified:
            refresh(request)
            auth.login(request, user)
            detail=wallet_details.objects.get(private_key=request.user.last_name)
            wallet=wallet_create_or_open(keys=detail.phrase,name=request.user.username,network='testnet',witness_type="segwit")
            print("[Wallet : ..... ]",wallet)
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
    if User.objects.filter(email=email).exists() and User.objects.get(email=email).is_verified:
        messages.info(request, 'Email Taken')
        return redirect('register')
    elif User.objects.filter(username=username).exists() and User.objects.get(username=username).is_verified:
        messages.info(request, 'Username Taken')
        return redirect('register')
    elif User.objects.filter(username=username).exists() and (not User.objects.filter(username=username).first().is_verified):
        user=User.objects.filter(username=username).values()
        token=TokenGenerator().make_token(user)
        s=send_verification_link(email,username,token)
        print(s)
        user.update(token=token)
        user.save()
        return redirect('login')
    else:
        token=TokenGenerator().make_token(user)
        user = User.objects.create_user(username=username, email=email, password=password,token=token)
        send_verification_link(email,username,token)
        user.save()
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
        amount=int(request.POST.get("amount"))
        bit_id=request.POST.get("bit_id")
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
    print(wallet)        
    return redirect("/")

def verify(request,token):
    user=User.objects.get(token=token)
    ch_token=TokenGenerator().check_token(user,token)
    if ch_token and (not user.is_verified):
        phrase=Mnemonic().generate()
        pickle.dump(file=open(request.user.username+'.pkl',"wb"),obj=phrase)
        wallet=wallet_create_or_open(keys=phrase,name=user.username,network='testnet',witness_type="segwit")
        key=wallet.get_key()
        w_details=wallet_details.objects.create(balance=wallet.balance(as_string=True),INR_balance=0,private_key=key.wif,phrase=phrase,address=key.address)
        w_details.save()
        user.update(is_verified=True,last_name=key.wif,first_name=key.address,token=None)
        user.save()

        address_data=address_book.objects.create(bit_id=user.username,Address=key.address)
        address_data.save()
    return redirect("login")


def forget_password(request):
    if request.method=="POST":
        u_name=request.POST.get("username")
        usr_obj=User.objects.filter(username=u_name)
        if usr_obj.exists():
            user=User.objects.get(username=u_name)
            token=TokenGenerator().make_token(user)
            send_reset_link(user.email,user.username,token)
            user.token=token
            user.save()
            messages.success(request, 'Email sent on your email')
            # return redirect("#")
        else:
            messages.info(request, 'User not found')
            return redirect("/forget")
    return render(request, 'reset_password.htm')

def reset(request,token):
    print("Password",request.POST.get("password1"))
    if request.method=="POST" and request.POST.get("password1")!=None:
        user=User.objects.filter(token=token).first()
        ch_token=TokenGenerator().check_token(user,token)
        if ch_token:
            password=request.POST.get("password1")
            usr_obj=User.objects.get(username=user.username)
            usr_obj.set_password(password)
            usr_obj.save()
        return redirect("login")

    user=User.objects.filter(token=token).first()
    ch_token=TokenGenerator().check_token(user,token)

    if ch_token:
        return render(request, 'reset_password.htm',{"ch_token":ch_token})
    else:
        messages.info(request, 'Invalid Link')
        return redirect("forget")
    return redirect("login")
