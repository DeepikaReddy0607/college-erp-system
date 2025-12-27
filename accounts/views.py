from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, authenticate
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Department, StudentProfile, FacultyProfile, OTPVerification

User = get_user_model()

def home_view(request):
    return redirect("login")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username = username, password=password)

        if user is None:
            return render(request, "auth/login.html", {
                "error": "Invalid credentials"
            })
        login(request, user)

        if user.role == "STUDENT":
            return redirect("dashboard")
        elif user.role == "FACULTY":
            return redirect("faculty_dashboard")
        else:
            return redirect("/admin/")

    return render(request, "auth/login.html")

def register_view(request):
    if request.method == "POST":
        role = request.POST.get("role").upper()
        fullname = request.POST.get("fullname")
        username = request.POST.get("username")
        email = request.POST.get("email")
        year = request.POST.get("year")
        sec = request.POST.get("section")

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "first_name": fullname,
                "role": role,
                "is_active": False,
                "is_verified": False,
            }
        )

        if not created and user.is_verified:
            return render(request, "auth/register.html", {
                "error": "Email already registered. Please login."
            })
        cse, _ = Department.objects.get_or_create(name="CSE")

        if role == "STUDENT":
            StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    "department": cse,
                    "year": year,
                    "section": sec
                }
            )
        elif role == "FACULTY":
            FacultyProfile.objects.get_or_create(
                user=user,
                defaults={
                    "department": cse,
                    "designation": "Faculty"
                }
            )
        OTPVerification.objects.filter(email=email, is_used=False).update(is_used=True)
        otp = get_random_string(length=4, allowed_chars="0123456789")
        OTPVerification.objects.create(email=email, otp=otp)

        send_mail(
            subject="Your ERP OTP Verification",
            message=f"Your OTP is {otp}",
            from_email="noreply@erp.com",
            recipient_list=[email],
        )
        request.session["email"] = email

        return redirect("otp")

    return render(request, 'auth/register.html')


def otp_view(request):
    if "email" not in request.session:
        return redirect("register")
    return render(request, "auth/otp.html")


@require_POST
def otp_verify_view(request):
    email = request.session.get("email")
    if not email:
        return redirect("register")

    otp_entered = (
        request.POST.get("otp1", "") +
        request.POST.get("otp2", "") +
        request.POST.get("otp3", "") +
        request.POST.get("otp4", "")
    )

    try:
        otp_record = OTPVerification.objects.get(
            email=email,
            otp=otp_entered,
            is_used=False
        )
    except OTPVerification.DoesNotExist:
        return render(request, "auth/otp.html", {"error": "Invalid OTP"})

    user = User.objects.get(email=email)
    user.is_active = True
    user.is_verified = True
    user.save()

    otp_record.is_used = True
    otp_record.save()

    return redirect("password")


def set_password_view(request):
    email = request.session.get("email")

    if not email:
        return redirect("register")

    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, "auth/password.html", {
                "error": "Passwords do not match"
            })

        user = User.objects.get(email=email)
        user.set_password(password)
        user.is_active = True
        user.save()

        login(request, user)
        request.session.flush()

        if user.role == "STUDENT":
            return redirect("dashboard")
        elif user.role == "FACULTY":
            return redirect("faculty_dashboard")
        else:
            return redirect("/admin/")

    return render(request, "auth/password.html")

@login_required
def dashboard_view(request):
    return render(request, 'dashboard/student_dashboard.html')