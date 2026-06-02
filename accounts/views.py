# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
import random    
from django.conf import settings
from django.contrib import messages
from .forms import SignUpForm
from .models import CustomUser

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False # Account abhi inactive rahega
            
            # Generate 6 Digit OTP
            otp = str(random.randint(100000, 999999))
            user.otp_code = otp
            user.save() # Isme tumhara form.save() method school bhi automatically create karega
            
            # Send Email (Tumhare settings me email configured hona zaroori hai)
            subject = f"Verify your account - {user.school.name}"
            message = f"Hello {user.first_name},\n\nYour verification code for School SaaS is: {otp}\n\nDo not share this with anyone."
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
                # Save user ID in session to verify later
                request.session['verification_user_id'] = user.id
                messages.info(request, f"We sent a 6-digit code to {user.email}")
                return redirect('verify_otp')
            except Exception as e:
                user.delete() # Agar email fail ho jaye to half-created user delete kar do
                messages.error(request, "Error sending email. Check internet or your email settings.")
        else:
            # Error hone par wapas page reload hota hai, errors form me dikhenge
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()
        
    return render(request, 'accounts/signup.html', {'form': form})

# --- OTP VERIFICATION VIEW ---
def verify_otp_view(request):
    user_id = request.session.get('verification_user_id')
    if not user_id:
        return redirect('signup')
        
    if request.method == 'POST':
        # OTP collect karne ka safe method
        entered_otp = "".join([request.POST.get(f'otp_{i}', '') for i in range(1, 7)])
        
        try:
            user = CustomUser.objects.get(id=user_id)
            if user.otp_code == entered_otp:
                user.is_active = True
                user.otp_code = None
                user.save()
                login(request, user)
                del request.session['verification_user_id']
                messages.success(request, "Account Verified! Welcome aboard.")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid OTP. Please try again.")
        except CustomUser.DoesNotExist:
            return redirect('signup')
            
    return render(request, 'accounts/verify_otp.html')

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})