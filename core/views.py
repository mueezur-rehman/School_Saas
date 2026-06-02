from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
import datetime
from django.db import transaction

# Imports from other apps
from academics.forms import ClassGradeForm, SectionForm, SubjectForm
from academics.models import ClassGrade, Section, Subject
from fees.forms import FeeStructureForm
from fees.models import FeeStructure, FeeCategory, FeePayment
from exams.forms import ExamForm
from exams.models import Exam
# Make sure StaffCreationForm is imported properly in your accounts app
from accounts.forms import StaffCreationForm 
from accounts.models import CustomUser
from students.models import Student
from expenses.models import Expense
from .forms import AcademicSessionForm
from .models import AcademicSession



def error_404_view(request, exception):
    return render(request, '404.html', status=404)

@login_required(login_url='login')
def manage_session(request):
    if not request.user.school:
        return redirect('login')
    sessions = AcademicSession.objects.filter(school=request.user.school).order_by('-start_date')
    return render(request, 'core/session_list.html', {'sessions': sessions})

# --- 1. HOME PAGE (LANDING PAGE) ---   
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

# --- 2. DASHBOARD VIEW ---
@login_required(login_url='login')
def dashboard(request):
    user = request.user
    
    # Boss Login Check
    if not user.school:
        if user.is_superuser:
            return render(request, 'core/dashboard.html', {'is_system_boss': True})
        return render(request, 'core/error.html', {'message': "Restricted Access. No school assigned."})

    # 🔥 SMART ONBOARDING REDIRECT
    active_session = AcademicSession.objects.filter(school=user.school, is_current=True).first()
    if not active_session:
        messages.warning(request, "Welcome! Please complete your quick school setup to activate your dashboard.")
        return redirect('master_setup')

    # Normal Dashboard Logic
    total_students = Student.objects.filter(school=user.school, status='active').count()
    total_classes = ClassGrade.objects.filter(school=user.school).count()
    
    today = timezone.now().date()
    todays_collection = FeePayment.objects.filter(school=user.school, payment_date=today).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    todays_expense = Expense.objects.filter(school=user.school, date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    net_cash = todays_collection - todays_expense

    labels, data = [], []
    current_date = today
    for i in range(5, -1, -1):
        month_start = (current_date.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        monthly_total = FeePayment.objects.filter(school=user.school, payment_date__range=[month_start, month_end]).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        labels.append(month_start.strftime("%b"))
        data.append(float(monthly_total))

    context = {
        'school_name': user.school.name,
        'total_students': total_students,
        'total_classes': total_classes,
        'todays_collection': todays_collection,
        'todays_expense': todays_expense,
        'net_cash': net_cash,
        'role': user.get_role_display(),
        'chart_labels': labels,
        'chart_data': data,
        'active_session': active_session,
    }
    return render(request, 'core/dashboard.html', context)

# --- 3. MASTER SETUP VIEW ---
@login_required(login_url='login')
def master_setup(request):
    user = request.user
    if not user.school:
        return render(request, 'core/error.html', {'message': "Restricted Access"})
    
    if user.role not in ['super_admin', 'school_admin']:
         return render(request, 'core/error.html', {'message': "Only Admins can access Setup."})

    # Check if session exists (To show either Wizard or Full Panel)
    active_session = AcademicSession.objects.filter(school=user.school, is_current=True).first()
    has_session = active_session is not None

    # 🚀 --- 1-CLICK ONBOARDING SETUP LOGIC ---
    if not has_session:
        if request.method == 'POST' and 'initial_setup' in request.POST:
            session_name = request.POST.get('session_name', '').strip()
            structure_type = request.POST.get('structure_type', 'standard')
            
            if not session_name:
                messages.error(request, "Please enter a valid session name.")
                return redirect('master_setup')

            try:
                with transaction.atomic():
                    # Generate Session
                    current_year = timezone.now().date().year
                    start_date = datetime.date(current_year, 4, 1)
                    end_date = datetime.date(current_year + 1, 3, 31)
                    
                    AcademicSession.objects.filter(school=user.school).update(is_current=False)
                    AcademicSession.objects.create(
                        school=user.school, name=session_name,
                        start_date=start_date, end_date=end_date, is_current=True
                    )
                    
                    # Generate Classes & Sections Based on Selection
                    if structure_type == 'madrasa':
                        classes_to_create = ['Qaida', 'Nazra', 'Hifz 1', 'Hifz 2', 'Deeniyat', 'Aalim Course']
                    else:
                        classes_to_create = ['Nursery', 'KG', 'Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5']
                    
                    for class_name in classes_to_create:
                        grade, _ = ClassGrade.objects.get_or_create(school=user.school, name=class_name)
                        Section.objects.get_or_create(school=user.school, class_grade=grade, name='A')
                        
                messages.success(request, f"Mubarak ho! {user.school.name} ka Setup 100% complete ho gaya hai.")
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f"Setup failed: {str(e)}")
        
        # Agar POST nahi hai, toh Wizard render karo
        return render(request, 'core/master_setup.html', {'has_session': has_session})


    # 🛠️ --- NORMAL MASTER CONFIGURATION LOGIC (Jab Setup ho chuka ho) ---
    class_form = ClassGradeForm(request.POST or None)
    section_form = SectionForm(user, request.POST or None)
    subject_form = SubjectForm(user, request.POST or None)
    exam_form = ExamForm(request.POST or None)
    fee_form = FeeStructureForm(user, request.POST or None)
    staff_form = StaffCreationForm(request.POST or None)

    active_tab = 'profile'

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            active_tab = 'profile'
            school = user.school
            school.name = request.POST.get('name')
            school.address = request.POST.get('address')
            school.phone = request.POST.get('phone')
            
            # 🚀 MAGIC FIX: Agar HTML form me institute_type nahi hai, toh purana wala hi rehne do
            new_type = request.POST.get('institute_type')
            if new_type:
                school.institute_type = new_type

            if request.FILES.get('logo'):
                school.logo = request.FILES['logo']
                
            school.save()
            messages.success(request, "Institute Profile Updated Successfully!")

        elif 'add_class' in request.POST:
            active_tab = 'academics'
            if class_form.is_valid():
                obj = class_form.save(commit=False)
                obj.school = user.school
                obj.save()
                messages.success(request, "Class/Batch Added!")
        
        elif 'add_section' in request.POST:
            active_tab = 'academics'
            if section_form.is_valid():
                obj = section_form.save(commit=False)
                obj.school = user.school
                obj.save()
                messages.success(request, "Section Added!")

        elif 'add_subject' in request.POST:
            active_tab = 'academics'
            if subject_form.is_valid():
                obj = subject_form.save(commit=False)
                obj.school = user.school
                obj.save()
                messages.success(request, "Subject Added!")

        elif 'add_exam' in request.POST:
            active_tab = 'exams'
            if exam_form.is_valid():
                obj = exam_form.save(commit=False)
                obj.school = user.school
                obj.save()
                messages.success(request, "Exam Created!")

        elif 'add_fee' in request.POST:
            active_tab = 'fees'
            if fee_form.is_valid():
                f_name = fee_form.cleaned_data['fee_head_name']
                category, created = FeeCategory.objects.get_or_create(
                    school=user.school, name__iexact=f_name, defaults={'name': f_name}
                )
                obj = fee_form.save(commit=False)
                obj.school = user.school
                obj.category = category
                obj.save()
                messages.success(request, f"Fee Structure Added!")

        elif 'add_staff' in request.POST:
            active_tab = 'staff'
            if staff_form.is_valid():
                obj = staff_form.save(commit=False)
                obj.school = user.school
                obj.save()
                messages.success(request, f"User {obj.username} created!")
                
        return redirect('master_setup')

    context = {
        'has_session': has_session,
        'school': user.school,
        'class_form': class_form,
        'section_form': section_form,
        'subject_form': subject_form,
        'exam_form': exam_form,
        'fee_form': fee_form,
        'staff_form': staff_form,
        'classes': ClassGrade.objects.filter(school=user.school),
        'exams': Exam.objects.filter(school=user.school),
        'fees': FeeStructure.objects.filter(school=user.school).select_related('category', 'class_grade'),
        'staff_list': CustomUser.objects.filter(school=user.school).exclude(role='student'),
        'active_tab': active_tab
    }
    return render(request, 'core/master_setup.html', context) 


    # 🛠️ --- NORMAL MASTER CONFIGURATION LOGIC (Jab Setup ho chuka ho) ---
    class_form = ClassGradeForm(request.POST or None)
    section_form = SectionForm(user, request.POST or None)
    subject_form = SubjectForm(user, request.POST or None)
    exam_form = ExamForm(request.POST or None)
    fee_form = FeeStructureForm(user, request.POST or None)
    staff_form = StaffCreationForm(request.POST or None)

    active_tab = 'profile'

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            active_tab = 'profile'
            school = user.school
            school.name = request.POST.get('name')
            school.address = request.POST.get('address')
            school.phone = request.POST.get('phone')
            school.institute_type = request.POST.get('institute_type')
            if request.FILES.get('logo'):
                school.logo = request.FILES['logo']
            school.save()
            messages.success(request, "Institute Profile Updated!")

        elif 'add_class' in request.POST:
            active_tab = 'academics'
            if class_form.is_valid():
                obj = class_form.save(commit=False)
                obj.school = user.school
                obj.save()
                messages.success(request, "Class/Batch Added!")
        
        elif 'add_section' in request.POST:
            active_tab = 'academics'
            if section_form.is_valid():
                obj = section_form.save(commit=False)
                obj.school = user.school
                obj.save()
                messages.success(request, "Section Added!")

        elif 'add_subject' in request.POST:
            active_tab = 'academics'
            if subject_form.is_valid():
                obj = subject_form.save(commit=False)
                obj.school = user.school
                obj.save()
                messages.success(request, "Subject Added!")

        elif 'add_exam' in request.POST:
            active_tab = 'exams'
            if exam_form.is_valid():
                obj = exam_form.save(commit=False)
                obj.school = user.school
                obj.save()
                messages.success(request, "Exam Created!")

        elif 'add_fee' in request.POST:
            active_tab = 'fees'
            if fee_form.is_valid():
                f_name = fee_form.cleaned_data['fee_head_name']
                category, created = FeeCategory.objects.get_or_create(
                    school=user.school, name__iexact=f_name, defaults={'name': f_name}
                )
                obj = fee_form.save(commit=False)
                obj.school = user.school
                obj.category = category
                obj.save()
                messages.success(request, f"Fee Structure Added!")

        elif 'add_staff' in request.POST:
            active_tab = 'staff'
            if staff_form.is_valid():
                obj = staff_form.save(commit=False)
                obj.school = user.school
                obj.save()
                messages.success(request, f"User {obj.username} created!")
                
        return redirect('master_setup')

    context = {
        'has_session': has_session,
        'school': user.school,
        'class_form': class_form,
        'section_form': section_form,
        'subject_form': subject_form,
        'exam_form': exam_form,
        'fee_form': fee_form,
        'staff_form': staff_form,
        'classes': ClassGrade.objects.filter(school=user.school),
        'exams': Exam.objects.filter(school=user.school),
        'fees': FeeStructure.objects.filter(school=user.school).select_related('category', 'class_grade'),
        'staff_list': CustomUser.objects.filter(school=user.school).exclude(role='student'),
        'active_tab': active_tab
    }
    return render(request, 'core/master_setup.html', context)

# --- 4. PROMOTE STUDENTS VIEW ---
@login_required(login_url='login')
def promote_students(request):
    if request.method == 'POST':
        from_class_id = request.POST.get('from_class')
        to_class_id = request.POST.get('to_class')
        student_ids = request.POST.getlist('student_ids')

        if from_class_id and to_class_id and student_ids:
            Student.objects.filter(id__in=student_ids, school=request.user.school).update(current_class_id=to_class_id)
            messages.success(request, f"Successfully promoted {len(student_ids)} students!")
            return redirect('promote_students')
    
    classes = ClassGrade.objects.filter(school=request.user.school)
    students = None
    selected_class = request.GET.get('from_class')
    if selected_class:
        students = Student.objects.filter(school=request.user.school, current_class_id=selected_class, status='active')

    return render(request, 'core/promote_students.html', {
        'classes': classes, 'students': students, 'selected_class': int(selected_class) if selected_class else None
    })

def subscription_expired(request):
    return render(request, 'core/subscription_expired.html')

def school_settings(request):
    return redirect('master_setup')