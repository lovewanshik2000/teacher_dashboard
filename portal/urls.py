from django.urls import path
from . import views

urlpatterns = [
    # Account management URLs
    path('signup/', views.signup_view, name='signup'),
    path('', views.login_view, name='login'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('logout/', views.logout_view, name='logout'),
    
    # Add other URLs for the portal app
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-student/', views.add_student, name='add_student'),
    path('update-student/<int:student_id>/', views.update_student, name='update_student'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
]
