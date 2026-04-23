from datetime import date
import logging
logger = logging.getLogger(__name__)
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model, login, authenticate, logout, update_session_auth_hash
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from academics.models import CourseOffering, FacultyAssignment
from accounts.forms import ProfileUpdateForm, StudentProfileImageForm
from assignments.models import Assignment, AssignmentSubmission
from examsection.models import ExamProfile
from timetable.models import TimetableEntry
from django.db.models import Q
from attendance.models import AttendanceRecord, AttendanceSession
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
    elif user.role == "EXAM_SECTION":
        return redirect("exam_dashboard")
    return redirect("/admin/")

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from .models import Department, OTPVerification
from accounts.tasks import send_verification_email_task

User = get_user_model()


from django.utils.crypto import get_random_string
from django.utils import timezone

def register_view(request):
    departments = Department.objects.all()

    if request.method == "POST":
        role = request.POST.get("role")
        fullname = request.POST.get("fullname", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        year = request.POST.get("year")
        sec = request.POST.get("section")
        dept_id = request.POST.get("department")

        if not role or not username or not email:
            return render(request, "auth/register.html", {
                "error": "All fields required", "departments": departments
            })

        if User.objects.filter(username=username).exists():
            return render(request, "auth/register.html", {
                "error": "Username exists", "departments": departments
            })

        existing = User.objects.filter(email=email).first()
        if existing and existing.is_verified:
            return render(request, "auth/register.html", {
                "error": "Email already registered", "departments": departments
            })

        otp = get_random_string(length=4, allowed_chars="0123456789")

        OTPVerification.objects.filter(email=email).delete()
        OTPVerification.objects.create(email=email, otp=otp, purpose="register")

        request.session["register_data"] = {
            "username": username,
            "email": email,
            "fullname": fullname,
            "role": role.upper(),
            "year": year,
            "section": sec,
            "department_id": dept_id
        }

        request.session["email"] = email
        request.session["otp_purpose"] = "register"

        send_verification_email_task(
            "OTP Verification",
            "email/otp_email.html",
            {"otp": otp, "user": {"username": username}},
            email
        )

        return redirect("otp")

    return render(request, "auth/register.html", {"departments": departments})


def otp_view(request):
    if "email" not in request.session:
        return redirect("login")
    return render(request, "auth/otp.html")

@require_POST
def otp_verify_view(request):
    email = request.session.get("email")
    purpose = request.session.get("otp_purpose")

    if not email or not purpose:
        return redirect("login")

    otp_entered = (
        request.POST.get("otp1", "") +
        request.POST.get("otp2", "") +
        request.POST.get("otp3", "") +
        request.POST.get("otp4", "")
    )

    otp = OTPVerification.objects.filter(
        email=email,
        otp=otp_entered,
        is_used=False,
        purpose=purpose
    ).first()

    if not otp:
        return render(request, "auth/otp.html", {"error": "Invalid OTP"})

    if (timezone.now() - otp.created_at).seconds > 600:
        return render(request, "auth/otp.html", {"error": "OTP expired"})

    otp.is_used = True
    otp.save()

    request.session["otp_verified"] = True

    # 🔥 CREATE USER ONLY HERE (NOT in password view)
    if purpose == "register":
        data = request.session.get("register_data")

        if not data:
            return redirect("register")

        user, created = User.objects.get_or_create(
            email=data["email"],
            defaults={
                "username": data["username"],
                "first_name": data["fullname"],
                "role": data["role"],
                "is_active": True,
                "is_verified": True,
            }
        )

        if not created:
            user.username = data["username"]
            user.is_verified = True
            user.save()

    return redirect("password")

def set_password_view(request):
    email = request.session.get("email")
    purpose = request.session.get("otp_purpose")
    otp_verified = request.session.get("otp_verified")

    if not otp_verified or not purpose:
        return redirect("login")

    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, "auth/password.html", {
                "error": "Passwords do not match"
            })

        user = User.objects.get(email=email)

        # 🔥 ONLY SET PASSWORD (NO USER CREATION HERE)
        user.set_password(password)
        user.is_verified = True
        user.save()

        # -------- CREATE PROFILE ONLY FOR REGISTER --------
        if purpose == "register":
            data = request.session.get("register_data")
            department = get_object_or_404(Department, id=data["department_id"])

            if user.role == "STUDENT":
                StudentProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "department": department,
                        "year": int(data["year"]),
                        "section": data["section"]
                    }
                )

            elif user.role == "FACULTY":
                FacultyProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "department": department,
                        "designation": "Faculty"
                    }
                )

        OTPVerification.objects.filter(email=email).delete()
        request.session.flush()

        login(request, user)
        return redirect_by_role(user)

    return render(request, "auth/password.html")

def resend_otp_view(request):
    email = request.session.get("email")
    purpose = request.session.get("otp_purpose")

    if not email or not purpose:
        return redirect("login")

    otp = get_random_string(length=4, allowed_chars="0123456789")

    OTPVerification.objects.filter(email=email).update(is_used=True)

    OTPVerification.objects.create(email=email, otp=otp, purpose=purpose)

    send_verification_email_task(
        "Resend OTP",
        "email/otp_email.html",
        {"otp": otp, "user": {"username": email}},
        email
    )

    return redirect("otp")

def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "auth/forgot_password.html", {
                "error": "No account found"
            })

        otp = get_random_string(length=4, allowed_chars="0123456789")

        OTPVerification.objects.filter(email=email).update(is_used=True)
        OTPVerification.objects.create(email=email, otp=otp, purpose="reset")

        request.session["email"] = email
        request.session["otp_purpose"] = "reset"

        send_verification_email_task(
            "Password Reset OTP",
            "email/otp_email.html",
            {"otp": otp, "user": {"username": user.username}},
            email
        )

        return redirect("otp")

    return render(request, "auth/forgot_password.html")

@login_required
def faculty_dashboard_view(request):

    if request.user.role != "FACULTY":
        return redirect("dashboard")

    faculty = request.user

    # ----------------------------------
    # Faculty Offerings
    # ----------------------------------
    faculty_assignments = FacultyAssignment.objects.filter(
        faculty=faculty
    )

    offerings = CourseOffering.objects.filter(
        id__in=faculty_assignments.values_list("offering_id", flat=True)
    ).select_related("course")

    # ----------------------------------
    # Stats Counts
    # ----------------------------------
    courses_count = offerings.count()

    today_code = date.today().strftime("%a").upper()[:3]

    todays_classes = TimetableEntry.objects.filter(
        offering__in=offerings,
        day=today_code
    ).select_related(
        "offering__course",
        "timeslot"
    ).order_by("timeslot__start_time")

    todays_classes_count = todays_classes.count()

    open_sessions = AttendanceSession.objects.filter(
        faculty=faculty,
        date=date.today(),
        status=AttendanceSession.STATUS_OPEN
    ).select_related("course_offering__course")

    pending_attendance_count = open_sessions.count()

    active_assignments = Assignment.objects.filter(
        offering__in=offerings,
        due_date__gte=date.today()
    ).select_related("offering__course").order_by("-created_at")[:5]

    active_assignments_count = active_assignments.count()

    notifications = Notification.objects.filter(
        Q(is_global=True) |
        Q(target_role="FACULTY") |
        Q(course_offering__in=offerings)
    ).order_by("-created_at")[:5]

    context = {
        "courses_count": courses_count,
        "todays_classes_count": todays_classes_count,
        "pending_attendance_count": pending_attendance_count,
        "active_assignments_count": active_assignments_count,
        "todays_classes": todays_classes,
        "open_sessions": open_sessions,
        "active_assignments": active_assignments,
        "notifications": notifications,
    }

    return render(request, "dashboard/faculty_dashboard.html", context)

@login_required
def faculty_courses_view(request):
    print("====================================")
    print("LOGGED IN USER:", request.user)
    print("LOGGED IN USER ID:", request.user.id)

    all_assignments = FacultyAssignment.objects.all()
    print("TOTAL FacultyAssignment COUNT:", all_assignments.count())

    user_assignments = FacultyAssignment.objects.filter(
        faculty=request.user
    )
    print("USER ASSIGNMENTS COUNT:", user_assignments.count())

    for a in all_assignments:
        print(
            "ASSIGNMENT → faculty:",
            a.faculty,
            "faculty_id:",
            a.faculty.id,
            "| offering:",
            a.offering
        )

    print("====================================")

    return render(
        request,
        "dashboard/my_courses.html",
        {
            "assignments": user_assignments
        }
    )


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

@login_required
def student_dashboard_view(request):
    user = request.user
    student = user.studentprofile

    # ------------------------------------------------
    # Get Active Course Offerings for This Student
    # ------------------------------------------------
    offerings = CourseOffering.objects.filter(
        department=student.department,
        year=student.year,
        section=student.section,
        is_active=True
    ).select_related("course")

    # ------------------------------------------------
    # Attendance Summary
    # ------------------------------------------------
    attendance_records = AttendanceRecord.objects.filter(
        student=user,
        session__course_offering__in=offerings
    ).select_related(
        "session__course_offering__course"
    )

    total_classes = attendance_records.count()

    present_count = attendance_records.filter(
        status=AttendanceRecord.STATUS_PRESENT
    ).count()

    overall_percentage = 0
    if total_classes > 0:
        overall_percentage = round(
            (present_count / total_classes) * 100, 2
        )

    if overall_percentage >= 75:
        status = "Safe"
        status_class = "safe"
    elif overall_percentage >= 65:
        status = "Warning"
        status_class = "warning"
    else:
        status = "Shortage"
        status_class = "danger"

    # ------------------------------------------------
    # Course-wise Attendance
    # ------------------------------------------------
    subject_attendance = []

    for offering in offerings:
        records = attendance_records.filter(
            session__course_offering=offering
        )

        total = records.count()
        present = records.filter(
            status=AttendanceRecord.STATUS_PRESENT
        ).count()

        percentage = 0
        if total > 0:
            percentage = round((present / total) * 100, 2)

        subject_attendance.append({
            "subject": offering.course.course_title,
            "percentage": percentage
        })

    # ------------------------------------------------
    # Today's Classes
    # ------------------------------------------------
    today_code = date.today().strftime("%a").upper()[:3]
    # MON, TUE, WED, etc.

    todays_classes = TimetableEntry.objects.filter(
        offering__in=offerings,
        day=today_code
    ).select_related(
        "offering__course",
        "timeslot"
    ).order_by("timeslot__start_time")

    # ------------------------------------------------
    # Pending Assignments
    # ------------------------------------------------
    assignments = Assignment.objects.filter(
        offering__in=offerings,
        due_date__gte=date.today()
    )

    submitted_ids = AssignmentSubmission.objects.filter(
        student=student
    ).values_list("assignment_id", flat=True)

    pending_assignments = assignments.exclude(
        id__in=submitted_ids
    )

    # ------------------------------------------------
    # Notifications
    # ------------------------------------------------
    notifications = Notification.objects.filter(
        Q(is_global=True) |
        Q(target_role="STUDENT") |
        Q(course_offering__in=offerings)
    ).order_by("-created_at")[:5]

    context = {
        "overall_percentage": overall_percentage,
        "status": status,
        "status_class": status_class,
        "subject_attendance": subject_attendance,
        "todays_classes": todays_classes,
        "pending_assignments": pending_assignments,
        "notifications": notifications,
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

@login_required
def profile_view(request):
    user = request.user

    context = {
        "user": user,
    }

    if user.role == "STUDENT":
        context["profile"] = StudentProfile.objects.get(user=user)
        return render(request, "student/student_profile.html", context)

    elif user.role == "FACULTY":
        context["profile"] = FacultyProfile.objects.get(user=user)
        return render(request, "faculty/faculty_profile.html", context)
    elif user.role == "EXAM_SECTION":
        context["profile"] = ExamProfile.objects.filter(user=user).first()
        return render(request, "exam/exam_profile.html", context)
    elif user.role == "ADMIN":
        return render(request, "admin_profile.html", context)

@login_required
def edit_profile(request):
    user = request.user

    if user.role == "STUDENT":
        profile = StudentProfile.objects.get(user=user)

        if request.method == "POST":
            user_form = ProfileUpdateForm(request.POST, instance=user)
            image_form = StudentProfileImageForm(
                request.POST,
                request.FILES,
                instance=profile
            )

            if user_form.is_valid() and image_form.is_valid():
                user_form.save()
                image_form.save()
                return redirect("profile")

        else:
            user_form = ProfileUpdateForm(instance=user)
            image_form = StudentProfileImageForm(instance=profile)

        return render(request, "accounts/edit_profile.html", {
            "user_form": user_form,
            "image_form": image_form
        })

@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)

        # 🔥 role-based redirect
        if request.user.role == "STUDENT":
            return redirect("student_dashboard")
        elif request.user.role == "FACULTY":
            return redirect("faculty_dashboard")
        elif request.user.role == "EXAM_SECTION":
            return redirect("exam_dashboard")
        elif request.user.role == "ADMIN":
            return redirect("admin_dashboard")

        return redirect("profile")

    # 🔥 role-based template
    role_templates = {
        "STUDENT": "student/change_password.html",
        "FACULTY": "faculty/change_password.html",
        "EXAM_SECTION": "exam/change_password.html",
        "ADMIN": "admin/change_password.html",
    }

    template_name = role_templates.get(
        request.user.role,
        "common/change_password.html"
    )

    return render(request, template_name, {"form": form})

@login_required
def upload_photo(request):

    if request.method == "POST":
        print("FILES:", request.FILES)
        profile = None

        # 🔥 Handle roles properly
        if request.user.role == "STUDENT":
            profile = StudentProfile.objects.filter(user=request.user).first()

        elif request.user.role == "FACULTY":
            profile = FacultyProfile.objects.filter(user=request.user).first()

        elif request.user.role == "EXAM_SECTION":
            profile = ExamProfile.objects.filter(user=request.user).first()

        # ❌ If no profile exists
        if not profile:
            return redirect("profile")

        # 🔥 Handle file upload
        file = request.FILES.get("profile_picture")
        print("FILE:", file) 
        if profile and file:
            profile.profile_picture = file
            profile.save()
            print("SAVED SUCCESS")

    return redirect("profile")