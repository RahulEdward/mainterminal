from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User
import http.client
import json
import uuid
from cryptography.fernet import Fernet
from django.conf import settings

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR', '0.0.0.0')

def get_mac_address():
    return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                    for elements in range(0,2*6,2)][::-1])

def authenticate_with_angel(client_id, pin, totp, api_key, client_local_ip, client_public_ip, mac_address):
    try:
        conn = http.client.HTTPSConnection("apiconnect.angelone.in")
        
        payload = json.dumps({
            "clientcode": client_id,
            "password": pin,
            "totp": totp,
            "state": "MAINTERMINAL"
        })

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UserType': 'USER',
            'X-SourceID': 'WEB',
            'X-ClientLocalIP': client_local_ip,
            'X-ClientPublicIP': client_public_ip,
            'X-MACAddress': mac_address,
            'X-PrivateKey': api_key
        }

        conn.request("POST", "/rest/auth/angelbroking/user/v1/loginByPassword", 
                    payload, headers)
        
        res = conn.getresponse()
        response = res.read().decode("utf-8")
        response_json = json.loads(response)
        
        if res.status == 200 and response_json.get('status'):
            return response_json['data']['jwtToken']
        return None
        
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        return None

def register(request):
    if request.method == "POST":
        try:
            username = request.POST.get("username")
            client_id = request.POST.get("client_id")
            api_key = request.POST.get("api_key")
            password = request.POST.get("password")  # If you're collecting password

            # Validate required fields
            if not all([username, client_id, api_key]):
                messages.error(request, "All fields are required!")
                return render(request, "users/register.html")

            # Check for existing username
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists!")
                return render(request, "users/register.html")
            
            # Check for existing client_id
            if User.objects.filter(client_id=client_id).exists():
                messages.error(request, "Client ID already exists!")
                return render(request, "users/register.html")

            # Create new user using CustomUserManager
            user = User.objects.create_user(
                username=username,
                client_id=client_id,
                api_key=api_key,
                password=password
            )
            
            messages.success(request, "Registration successful! Please login.")
            return redirect("login")
            
        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            return render(request, "users/register.html")
            
    return render(request, "users/register.html")

def login_view(request):
    if request.method == "POST":
        client_id = request.POST.get("client_id")
        pin = request.POST.get("pin")
        totp_code = request.POST.get("totp_code")

        if not all([client_id, pin, totp_code]):
            messages.error(request, "All fields are required!")
            return render(request, "users/login.html")

        try:
            user = User.objects.get(client_id=client_id)
            
            # Get API key for authentication
            api_key = user.api_key  # API key is stored directly now
            
            jwt_token = authenticate_with_angel(
                client_id=client_id,
                pin=pin,
                totp=totp_code,
                api_key=api_key,
                client_local_ip=get_client_ip(request),
                client_public_ip=get_client_ip(request),
                mac_address=get_mac_address()
            )
            
            if jwt_token:
                user.access_token = jwt_token
                user.save()
                request.session["user_id"] = user.id
                messages.success(request, "Login successful!")
                return redirect("dashboard")
            else:
                messages.error(request, "Authentication failed with AngelOne API")
                
        except User.DoesNotExist:
            messages.error(request, "Invalid client ID!")
        except Exception as e:
            messages.error(request, f"Login failed: {str(e)}")
            
    return render(request, "users/login.html")

def dashboard(request):
    if "user_id" not in request.session:
        return redirect("login")

    try:
        user = User.objects.get(id=request.session["user_id"])
        if not user.access_token:
            messages.error(request, "Your session has expired. Please login again.")
            return redirect("login")
            
        context = {
            "user": user,
            "client_id": user.client_id,
        }
        return render(request, "users/dashboard.html", context)
    except User.DoesNotExist:
        return redirect("login")

def logout(request):
    if "user_id" in request.session:
        try:
            user = User.objects.get(id=request.session["user_id"])
            user.access_token = None
            user.save()
            del request.session["user_id"]
            messages.success(request, "Logged out successfully!")
        except User.DoesNotExist:
            messages.error(request, "User not found!")
        except Exception as e:
            messages.error(request, f"Logout failed: {str(e)}")
    
    return redirect("login")