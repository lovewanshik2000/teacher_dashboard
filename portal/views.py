from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from .models import Teacher, Student
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.paginator import Paginator

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if Teacher.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "signup.html")

        Teacher.objects.create(
            username=username,
            password=make_password(password)
        )
        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")

    return render(request, "signup.html")


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            teacher = Teacher.objects.get(username=username, is_deleted=False, is_active=True)
            if check_password(password, teacher.password):
                request.session['teacher_id'] = teacher.id
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid password")
        except Teacher.DoesNotExist:
            messages.error(request, "User does not exist")
    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


def forgot_password_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        new_password = request.POST.get("new_password")

        try:
            teacher = Teacher.objects.get(username=username, is_deleted=False)
            teacher.password = make_password(new_password)
            teacher.save()
            messages.success(request, "Password reset successfully. Please login.")
            return redirect('login')
        except Teacher.DoesNotExist:
            messages.error(request, "User not found.")
            return render(request, "forgot_password.html")

    return render(request, "forgot_password.html")


def dashboard(request):
    if not request.session.get('teacher_id'):
        return redirect('login')

    teacher = get_object_or_404(Teacher, id=request.session['teacher_id'], is_deleted=False)
    # students_list = Student.objects.filter(is_deleted=False, created_by=teacher).order_by('-created_at')
    students_list = Student.objects.filter(is_deleted=False).order_by('-created_at')
    
    
    # Pagination (10 per page)
    paginator = Paginator(students_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard.html', {'page_obj': page_obj})


@csrf_exempt
def add_student(request):
    if request.method == 'POST':
        try:
            teacher_id = request.session.get("teacher_id")
            if not teacher_id:
                return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)

            teacher = get_object_or_404(Teacher, id=teacher_id, is_deleted=False)

            data = json.loads(request.body)
            name = data.get("name", "").strip()
            subject = data.get("subject", "").strip()
            marks_raw = data.get("marks", "").strip()

            if not name or not subject or not marks_raw:
                return JsonResponse({'status': 'error', 'message': 'All fields are required.'}, status=400)

            try:
                marks = int(marks_raw)
                if marks < 0:
                    return JsonResponse({'status': 'error', 'message': 'Marks must be non-negative.'}, status=400)
            except ValueError:
                return JsonResponse({'status': 'error', 'message': 'Marks must be an integer.'}, status=400)

            # Check if student already exists for same teacher
            student, created = Student.objects.get_or_create(
                name=name,
                subject=subject,
                is_deleted=False,
                created_by=teacher,
                defaults={
                    'marks': marks,
                }
            )

            if not created:
                student.marks = marks
                student.updated_by = teacher
                student.save()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


@csrf_exempt
def update_student(request, student_id):
    if request.method == 'POST':
        try:
            teacher_id = request.session.get("teacher_id")
            if not teacher_id:
                return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)

            teacher = get_object_or_404(Teacher, id=teacher_id, is_deleted=False)
            student = get_object_or_404(Student, id=student_id, is_deleted=False, created_by=teacher)

            data = json.loads(request.body)
            name = data.get("name", "").strip()
            subject = data.get("subject", "").strip()
            marks_raw = data.get("marks", "").strip()

            if not name or not subject or not marks_raw:
                return JsonResponse({'status': 'error', 'message': 'All fields are required.'}, status=400)

            try:
                marks = int(marks_raw)
                if marks < 0:
                    return JsonResponse({'status': 'error', 'message': 'Marks must be non-negative.'}, status=400)
            except ValueError:
                return JsonResponse({'status': 'error', 'message': 'Marks must be an integer.'}, status=400)

            student.name = name
            student.subject = subject
            student.marks = marks
            student.updated_by = teacher  # ✅ Set updated_by only on update
            student.save()

            return JsonResponse({'status': 'updated'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


@csrf_exempt
def delete_student(request, student_id):
    if request.method == 'POST':
        try:
            teacher_id = request.session.get("teacher_id")
            if not teacher_id:
                return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)

            teacher = get_object_or_404(Teacher, id=teacher_id, is_deleted=False)
            student = get_object_or_404(Student, id=student_id, is_deleted=False, created_by=teacher)
            student.is_deleted = True
            student.updated_by = teacher  # ✅ Optionally set updated_by on deletion
            student.save()

            return JsonResponse({'status': 'deleted'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)
