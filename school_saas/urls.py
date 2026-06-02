from django.contrib import admin
from core.views import * 
from django.urls import path
from django.contrib.auth import views as auth_views 
from django.conf import settings
from django.conf.urls.static import static

# ==========================================
# 🚀 LEADSBYTECH ERP - ALL APP VIEWS IMPORTS
# ==========================================
from core.views import home, dashboard, master_setup, promote_students, subscription_expired, manage_session
from accounts.views import signup_view, verify_otp_view, change_password
from students.views import (
    student_admission, student_list, student_edit, 
    generate_id_card, bulk_upload_students,
    student_profile, student_fee_ledger, print_admission_form
)
from fees.views import collect_fees, payment_receipt, defaulter_list
from attendance.views import take_attendance
from exams.views import (
    enter_marks, generate_report_card, result_list, 
    download_marks_template, bulk_upload_marks
)
from expenses.views import expense_list, delete_expense


# 🛡️ Custom Error Handlers (Make sure error_404_view exists in core/views.py)
handler404 = 'core.views.error_404_view'

urlpatterns = [
    # 🔒 SECURE ADMIN URL (Hacker Protection)
    path('leadsbytech-secure-admin/', admin.site.urls),
    
    # 🔑 AUTHENTICATION SYSTEM
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('signup/', signup_view, name='signup'), 
    path('account/password/', change_password, name='change_password'),
    path('verify-otp/', verify_otp_view, name='verify_otp'),

    # 🏠 CORE & DASHBOARD
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('setup/master/', master_setup, name='master_setup'),
    path('students/promote/', promote_students, name='promote_students'),
    path('subscription-expired/', subscription_expired, name='subscription_expired'),
    path('settings/sessions/', manage_session, name='manage_sessions'),

    # 🎓 STUDENTS MANAGEMENT
    path('admission/new/', student_admission, name='student_admission'),
    path('students/', student_list, name='student_list'),
    path('student/edit/<int:pk>/', student_edit, name='student_edit'),
    path('student/profile/<int:pk>/', student_profile, name='student_profile'),
    path('student/id-card/<int:pk>/', generate_id_card, name='generate_id_card'),
    path('students/bulk-upload/', bulk_upload_students, name='bulk_upload_students'),
    path('student/ledger/<int:pk>/', student_fee_ledger, name='student_fee_ledger'),
    path('student/print-form/<int:pk>/', print_admission_form, name='print_admission_form'),

    # 💰 FEES & EXPENSES ENGINE
    path('fees/collect/', collect_fees, name='collect_fees'),
    path('fees/receipt/<int:pk>/', payment_receipt, name='payment_receipt'),
    path('fees/defaulters/', defaulter_list, name='defaulter_list'),
    path('expenses/', expense_list, name='expense_list'),
    path('expenses/delete/<int:pk>/', delete_expense, name='delete_expense'),

    # 📚 ACADEMICS, ATTENDANCE & EXAMS
    path('attendance/take/', take_attendance, name='take_attendance'),
    path('exams/marks/', enter_marks, name='enter_marks'),
    path('exams/results/', result_list, name='result_list'),
    path('exams/report/<int:student_id>/<int:exam_id>/', generate_report_card, name='student_report_card'),
    path('exams/download-template/', download_marks_template, name='download_marks_template'),
    path('exams/bulk-upload-marks/', bulk_upload_marks, name='bulk_upload_marks'),
]

# 📁 MEDIA & STATIC FILES ROUTING FOR DEVELOPMENT
# (Production mein yeh Whitenoise handle karega, but local ke liye zaroori hai)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)