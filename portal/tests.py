from django.test import TestCase, Client
from django.urls import reverse
from .models import Teacher, Student
from django.contrib.auth.hashers import check_password, make_password
import json
class TeacherModelTest(TestCase):
    def test_create_teacher(self):
        teacher = Teacher.objects.create(username="john_doe", password="hashed")
        self.assertEqual(str(teacher), "john_doe")
        self.assertFalse(teacher.is_deleted)
        self.assertTrue(teacher.is_active)

class StudentModelTest(TestCase):
    def setUp(self):
        self.teacher = Teacher.objects.create(username="teacher1", password="pwd")

    def test_create_student(self):
        student = Student.objects.create(name="Alice", subject="Math", marks=90, created_by=self.teacher)
        self.assertEqual(str(student), "Alice - Math")
        self.assertFalse(student.is_deleted)

    def test_unique_constraint(self):
        Student.objects.create(name="Alice", subject="Math", marks=85)
        with self.assertRaises(Exception):
            Student.objects.create(name="Alice", subject="Math", marks=90)


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse("signup")
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.forgot_password_url = reverse("forgot_password")
        self.dashboard_url = reverse("dashboard")
        self.add_student_url = reverse("add_student")

        # ✅ Correctly hash the password using Django's password hasher
        self.teacher = Teacher.objects.create(
            username="teacher1",
            password=make_password("test123")  # match this in login test
        )

    def test_signup(self):
        response = self.client.post(self.signup_url, {'username': 'new_user', 'password': 'new_pass'})
        self.assertEqual(response.status_code, 302)  # Redirect after signup
        self.assertTrue(Teacher.objects.filter(username='new_user').exists())

    def test_login_success(self):
        response = self.client.post(self.login_url, {
            'username': self.teacher.username,
            'password': 'test123'  # Match the hashed password
        })
        # Expect redirect to dashboard (if successful)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_fail(self):
        response = self.client.post(self.login_url, {'username': 'fake', 'password': 'wrong'})
        self.assertContains(response, "User does not exist")

    def test_logout(self):
        session = self.client.session
        session['teacher_id'] = self.teacher.id
        session.save()
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)

    def test_forgot_password(self):
        response = self.client.post(self.forgot_password_url, {
            'username': self.teacher.username,
            'new_password': 'newpass'
        })
        self.assertRedirects(response, self.login_url)

    def test_dashboard_requires_login(self):
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, self.login_url)

    def test_dashboard_view(self):
        session = self.client.session
        session['teacher_id'] = self.teacher.id
        session.save()
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)

    def test_add_student(self):
        session = self.client.session
        session['teacher_id'] = self.teacher.id
        session.save()

        data = {
            'name': 'Student 1',
            'subject': 'Math',
            'marks': '85'
        }
        response = self.client.post(self.add_student_url, data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Student.objects.count(), 1)

    def test_update_student(self):
        student = Student.objects.create(name="Old", subject="History", marks=50, created_by=self.teacher)
        update_url = reverse("update_student", args=[student.id])

        session = self.client.session
        session['teacher_id'] = self.teacher.id
        session.save()

        new_data = {
            'name': 'Updated Name',
            'subject': 'Geography',
            'marks': '78'
        }
        response = self.client.post(update_url, data=json.dumps(new_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        student.refresh_from_db()
        self.assertEqual(student.name, "Updated Name")

    def test_delete_student(self):
        student = Student.objects.create(name="Delete", subject="English", marks=70, created_by=self.teacher)
        delete_url = reverse("delete_student", args=[student.id])

        session = self.client.session
        session['teacher_id'] = self.teacher.id
        session.save()

        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 200)
        student.refresh_from_db()
        self.assertTrue(student.is_deleted)
