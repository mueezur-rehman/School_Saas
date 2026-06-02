from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentAdmissionForm
from django.db.models import Q 
from .models import Student, ClassGrade, Section
from core.models import AcademicSession 
import pandas as pd
from django.conf import settings
import os 
from django.utils import timezone
import datetime

from fees.models import FeePayment, FeeStructure
from django.db.models import Sum

# --- HELPER FUNCTION ---
def get_current_session(school):
    session = AcademicSession.objects.filter(school=school, is_current=True).first()
    return session

@login_required(login_url='login')
def student_admission(request):
    if not request.user.school:
        return render(request, 'core/error.html', {'message': "Restricted Access"})

    current_session = get_current_session(request.user.school)
    if not current_session:
        return render(request, 'core/error.html', {
            'message': "⚠️ No Active Academic Session Found! Please go to Admin Panel > Core > Academic Sessions and create a session."
        })

    if request.method == 'POST':
        form = StudentAdmissionForm(request.POST, request.FILES, school=request.user.school)
        if form.is_valid():
            student = form.save(commit=False)
            student.school = request.user.school
            student.session = current_session 
            student.admission_date = timezone.now().date() # Auto Date Fix
            student.save()
            
            messages.success(request, f"Success! {student.first_name} admitted successfully. Please print the form.")
            
            # 🚀 REDIRECT TO PDF PRINT PAGE
            return redirect('print_admission_form', pk=student.id)
    else:
        form = StudentAdmissionForm(school=request.user.school)

    return render(request, 'students/admission_form.html', {'form': form})

@login_required(login_url='login')
def student_list(request):
    if not request.user.school:
        return render(request, 'core/error.html', {'message': "Restricted Access"})

    students = Student.objects.filter(school=request.user.school).select_related('current_class', 'section', 'session')

    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) |
            Q(admission_no__icontains=search_query) |
            Q(father_mobile__icontains=search_query)
        )

    context = {
        'students': students,
        'search_query': search_query
    }
    return render(request, 'students/student_list.html', context)

@login_required(login_url='login')
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk, school=request.user.school)

    if request.method == 'POST':
        form = StudentAdmissionForm(request.POST, request.FILES, instance=student, school=request.user.school)
        if form.is_valid():
            form.save()
            messages.success(request, "Student details updated successfully!")
            return redirect('student_list')
    else:
        form = StudentAdmissionForm(instance=student, school=request.user.school)

    return render(request, 'students/edit_student.html', {'form': form, 'student': student})

@login_required(login_url='login')
def generate_id_card(request, pk):
    user = request.user
    if not user.school:
        return render(request, 'core/error.html', {'message': "Restricted Access"})

    student = get_object_or_404(Student, pk=pk, school=user.school)
    
    context = {
        'student': student,
        'school': user.school
    }
    return render(request, 'students/id_card.html', context)

@login_required(login_url='login')
def bulk_upload_students(request):
    user = request.user
    if not user.school:
        return render(request, 'core/error.html', {'message': "Restricted Access"})

    current_session = get_current_session(user.school)
    if not current_session:
        messages.error(request, "⚠️ Error: Active Academic Session nahi mila.")
        return redirect('student_list')

    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            messages.error(request, "Please upload a valid Excel file.")
            return redirect('bulk_upload_students')

        try:
            df = pd.read_excel(excel_file, dtype=str)
            df.columns = df.columns.str.strip()
            
            required_columns = ['First Name', 'Admission No', 'Class', 'Father Name', 'Mobile']
            missing_cols = [col for col in required_columns if col not in df.columns]
            
            if missing_cols:
                messages.error(request, f"Excel me ye columns nahi mile: {', '.join(missing_cols)}")
                return redirect('bulk_upload_students')

            success_count = 0
            skipped_rows = []

            for index, row in df.iterrows():
                row_num = index + 2
                
                def clean_val(val):
                    if pd.isna(val) or str(val).lower() == 'nan': return ''
                    return str(val).strip()

                first_name = clean_val(row.get('First Name'))
                last_name = clean_val(row.get('Last Name'))
                adm_no = clean_val(row.get('Admission No'))
                roll_no_str = clean_val(row.get('Roll Number'))
                class_name = clean_val(row.get('Class'))
                section_name = clean_val(row.get('Section'))
                
                father_name = clean_val(row.get('Father Name'))
                mother_name = clean_val(row.get('Mother Name'))
                father_mobile = clean_val(row.get('Mobile'))
                
                gender_raw = clean_val(row.get('Gender'))
                aadhar = clean_val(row.get('Aadhar No'))
                category = clean_val(row.get('Category'))
                religion = clean_val(row.get('Religion'))
                blood_group = clean_val(row.get('Blood Group'))

                if not first_name or not adm_no or not class_name:
                    skipped_rows.append(f"Row {row_num}: Name, Class ya Admission No missing.")
                    continue

                try:
                    class_obj = ClassGrade.objects.filter(school=user.school, name__iexact=class_name).first()
                    if not class_obj:
                        skipped_rows.append(f"Row {row_num}: Class '{class_name}' not found.")
                        continue

                    section_obj = None
                    if section_name:
                        section_obj = Section.objects.filter(school=user.school, name__iexact=section_name, class_grade=class_obj).first()

                    gender_code = 'M'
                    if gender_raw:
                        if gender_raw.lower().startswith('f'): gender_code = 'F'
                        elif gender_raw.lower().startswith('o'): gender_code = 'O'

                    roll_number = None
                    if roll_no_str:
                        try:
                            roll_number = int(float(roll_no_str))
                        except:
                            roll_number = None

                    Student.objects.update_or_create(
                        school=user.school,
                        admission_no=adm_no,
                        defaults={
                            'first_name': first_name,
                            'last_name': last_name,
                            'roll_number': roll_number,
                            'current_class': class_obj,
                            'section': section_obj,
                            'session': current_session,
                            'father_name': father_name,
                            'mother_name': mother_name,
                            'father_mobile': father_mobile,
                            'gender': gender_code,
                            'aadhar_no': aadhar,
                            'category': category,
                            'religion': religion,
                            'blood_group': blood_group,
                            'admission_date': timezone.now().date(),
                            'address': 'Address Update Pending'
                        }
                    )
                    success_count += 1

                except Exception as e:
                    skipped_rows.append(f"Row {row_num} Error: {str(e)}")

            if success_count > 0:
                messages.success(request, f"Imported {success_count} students in Session {current_session.name}!")
            
            if skipped_rows:
                messages.warning(request, "Skipped Rows:<br>" + "<br>".join(skipped_rows[:10]))

            return redirect('student_list')

        except Exception as e:
            messages.error(request, f"Critical Error: {str(e)}")
            return redirect('bulk_upload_students')

    return render(request, 'students/bulk_upload.html')

@login_required(login_url='login')
def student_profile(request, pk):
    student = get_object_or_404(Student, pk=pk, school=request.user.school)
    return render(request, 'students/student_profile.html', {'student': student})

@login_required(login_url='login')
def student_fee_ledger(request, pk):
    student = get_object_or_404(Student, pk=pk, school=request.user.school)
    payments = FeePayment.objects.filter(student=student).order_by('-payment_date')
    total_paid = payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    structures = FeeStructure.objects.filter(class_grade=student.current_class, school=request.user.school)
    total_payable = structures.aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_payable - total_paid

    context = {
        'student': student,
        'payments': payments,
        'total_paid': total_paid,
        'total_payable': total_payable,
        'balance': balance
    }
    return render(request, 'students/student_ledger.html', context)

@login_required(login_url='login')
def print_admission_form(request, pk):
    student = get_object_or_404(Student, pk=pk, school=request.user.school)
    return render(request, 'students/print_admission_form.html', {'student': student})