from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Department, StudentProfile, FacultyProfile, OTPVerification
from django.contrib import messages
from notifications.models import Notification, NotificationRecipient
User = get_user_model()

def home_view(request):
    return redirect("login")

def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username = username, password=password)

        if user is None:
            return render(request, "auth/login.html", {
                "error": "Invalid credentials"
            })
        
        if not user.is_active:
            return render(request, "auth/login.html",{
                "error": "Account not activated"
            })
        login(request, user)
        return redirect_by_role(user)
    return render(request, "auth/login.html")

def redirect_by_role(user):
    if user.role == "FACULTY":
        return redirect("faculty_dashboard")
    elif user.role == "STUDENT":
        return redirect("dashboard")
    return redirect("/admin/")

def register_view(request):
    if request.method == "POST":
        role = request.POST.get("role").upper()
        fullname = request.POST.get("fullname")
        username = request.POST.get("username").strip()
        email = request.POST.get("email").strip().lower()
        year = request.POST.get("year")
        sec = request.POST.get("section")

        if User.objects.filter(username=username).exists():
            return render(request, "auth/register.html", {
                "error": "Username already exists. Please choose another."
            })

        user = User.objects.filter(email=email).first()
        if user:
            if user.is_verified:
                return render(request, "auth/register.html", {
                    "error": "Email already registered. Please login."
                })
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=fullname,
                role=role,
                is_active=False,
                is_verified=False
            )

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

        OTPVerification.objects.filter(
            email=email,
            is_used=False
        ).update(is_used=True)

        otp = get_random_string(length=4, allowed_chars="0123456789")
        OTPVerification.objects.create(email=email, otp=otp)

        send_mail(
            subject="Your ERP OTP Verification",
            message=f"Your OTP is {otp}",
            from_email="noreply@erp.com",
            recipient_list=[email],
        )

        request.session["email"] = email
        request.session["otp_purpose"] = "register"

        return redirect("otp")

    return render(request, "auth/register.html")

def otp_view(request):
    if "email" not in request.session and "reset_email" not in request.session:
        return redirect("login")
    return render(request, "auth/otp.html")


@require_POST
def otp_verify_view(request):
    email = request.session.get("email") or request.session.get("reset_email")
    purpose = request.session.get("otp_purpose")

    if not email or not purpose:
        return redirect("login")

    otp_entered = (
        request.POST.get("otp1", "") +
        request.POST.get("otp2", "") +
        request.POST.get("otp3", "") +
        request.POST.get("otp4", "")
    )

    try:
        otp = OTPVerification.objects.get(
            email=email,
            otp=otp_entered,
            is_used=False
        )
    except OTPVerification.DoesNotExist:
        return render(request, "auth/otp.html", {"error": "Invalid OTP"})

    otp.is_used = True
    otp.save()

    if purpose == "register":
        return redirect("password")

    if purpose == "reset":
        return redirect("password")

    return redirect("login")


def set_password_view(request):
    email = request.session.get("email") or request.session.get("reset_email")

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
        request.session.pop("email", None)
        request.session.pop("reset_email", None)
        request.session.pop("otp_purpose", None)

        if user.role == "STUDENT":
            return redirect("dashboard")
        elif user.role == "FACULTY":
            return redirect("faculty_dashboard")
        else:
            return redirect("/admin/")

    return render(request, "auth/password.html")

@login_required
def faculty_dashboard_view(request):
    if request.user.role != "FACULTY":
        return redirect("dashboard")
    return render(request, "dashboard/faculty_dashboard.html")

@login_required
def faculty_courses_view(request):
    return render(request, "dashboard/my_courses.html")

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def faculty_attendance_mark_view(request):
    return render(request, 'dashboard/faculty_attendance.html')

@login_required
def faculty_attendance_history_view(request):
    return render(request, 'dashboard/faculty_attendance_history.html')

@login_required
def faculty_attendance_edit_view(request):
    return render(request, "dashboard/faculty_attendance_edit.html")

def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "auth/forgot_password.html", {
                "error": "No account found with this email"
            })

        otp = get_random_string(length=4, allowed_chars="0123456789")
        OTPVerification.objects.filter(email=email).update(is_used=True)
        OTPVerification.objects.create(email=email, otp=otp)

        send_mail(
            subject="ERP Password Reset OTP",
            message=f"Your OTP is {otp}",
            from_email="noreply@erp.com",
            recipient_list=[email],
        )

        request.session["reset_email"] = email
        request.session["otp_purpose"] = "reset"
        return redirect("otp")  

    return render(request, "auth/forgot_password.html")

@login_required
def student_dashboard_view(request):
    unread_notifications_count = NotificationRecipient.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    context = {
        "unread_notifications_count": unread_notifications_count,
    }
    return render(request, "student/dashboard.html", context)

@login_required
def dashboard_view(request):
    """
    Central dashboard router
    """
    if request.user.role == "STUDENT":
        return redirect("student_dashboard")
    elif request.user.role == "FACULTY":
        return redirect("faculty_dashboard")
    elif request.user.role == "ADMIN":
        return redirect("admin_dashboard")
    return redirect("login")