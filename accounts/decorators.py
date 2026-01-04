from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def faculty_required(view_func):
    @login_required
    def _wrapped(request, *args, **kwargs):
        if request.user.role != "FACULTY":
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped

def student_required(view_func):
    @login_required
    def _wrapped(request, *args, **kwargs):
        if request.user.role != "STUDENT":
            return redirect("faculty_dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped