from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academics.models import ClassGrade, Subject
from students.models import Student
from .models import Exam, StudentResult
from django.db.models import Sum
from django.http import HttpResponse
import pandas as pd

# --- 1. ENTER MARKS VIEW (SMART TABS + MANUAL) ---
@login_required(login_url='login')
def enter_marks(request):
    user = request.user
    if not user.school:
        return render(request, 'core/error.html', {'message': "Restricted Access"})

    # Dropdowns ke liye Sirf Exams aur Classes (Subject nahi)
    exams = Exam.objects.filter(school=user.school).order_by('-start_date')
    classes = ClassGrade.objects.filter(school=user.school).order_by('name')
    
    # Selections Get Karo (GET or POST)
    sel_exam = request.GET.get('exam') or request.POST.get('exam_id')
    sel_class = request.GET.get('class_grade') or request.POST.get('class_grade')
    sel_subject = request.GET.get('subject') or request.POST.get('subject_id')

    # Integers me convert (Safety)
    try: sel_exam = int(sel_exam) if sel_exam else None
    except: sel_exam = None
    
    try: sel_class = int(sel_class) if sel_class else None
    except: sel_class = None
    
    try: sel_subject = int(sel_subject) if sel_subject else None
    except: sel_subject = None

    subjects = []
    students_data = []
    current_subject = None

    # 🟢 MAGIC LOGIC: Sirf Selected Class ke Subjects nikalo
    if sel_class:
        subjects = Subject.objects.filter(school=user.school, class_grade_id=sel_class)
        
    # Agar teeno cheezein select hain (Manual Entry ke liye)
    if sel_exam and sel_class and sel_subject:
        current_subject = subjects.filter(id=sel_subject).first()
        
        if current_subject: # Security check: Kya ye subject is class ka hai?
            students = Student.objects.filter(
                school=user.school, 
                current_class_id=sel_class, 
                status='active'
            ).order_by('roll_number')

            for student in students:
                result = StudentResult.objects.filter(
                    exam_id=sel_exam,
                    subject_id=sel_subject,
                    student=student
                ).first()
                
                students_data.append({
                    'student': student,
                    'marks': result.marks_obtained if result else ''
                })

        # --- SAVE LOGIC (Manual Entry POST) ---
        if request.method == 'POST' and 'save_marks' in request.POST:
            success_count = 0
            for item in students_data:
                std_id = item['student'].id
                input_name = f"marks_{std_id}"
                marks_val = request.POST.get(input_name)

                if marks_val and marks_val.strip():
                    try:
                        val = float(marks_val)
                        if val <= current_subject.total_marks:
                            StudentResult.objects.update_or_create(
                                school=user.school,
                                exam_id=sel_exam,
                                subject_id=sel_subject,
                                student_id=std_id,
                                defaults={
                                    'marks_obtained': val,
                                    'total_marks': current_subject.total_marks
                                }
                            )
                            success_count += 1
                    except ValueError:
                        pass
            
            messages.success(request, f"✅ Saved marks for {current_subject.name}!")
            return redirect(f"{request.path}?exam={sel_exam}&class_grade={sel_class}&subject={sel_subject}")

    context = {
        'exams': exams,
        'classes': classes,
        'subjects': subjects, # Yeh ab FILTERED list hai (Sirf us class ki)
        
        'sel_exam': sel_exam,
        'sel_class': sel_class,
        'sel_subject': sel_subject,
        
        'students_data': students_data,
        'current_subject': current_subject
    }
    return render(request, 'exams/enter_marks.html', context)


# --- 2. DOWNLOAD MASTER EXCEL (Class Wise) ---
@login_required(login_url='login')
def download_marks_template(request):
    class_id = request.GET.get('class_grade')
    if not class_id:
        messages.error(request, "Please select a Class first.")
        return redirect('enter_marks')

    students = Student.objects.filter(school=request.user.school, current_class_id=class_id, status='active').order_by('roll_number')
    subjects = Subject.objects.filter(school=request.user.school, class_grade_id=class_id).order_by('name')

    if not subjects.exists():
        messages.error(request, "This Class has no subjects!")
        return redirect('enter_marks')

    data = []
    for std in students:
        row = {
            'Admission No': std.admission_no,
            'Roll No': std.roll_number,
            'Student Name': f"{std.first_name} {std.last_name}",
        }
        for sub in subjects:
            row[sub.name] = '' # Empty column for marks
        data.append(row)

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Marks_Entry_Template.xlsx"'
    df.to_excel(response, index=False)
    return response


# --- 3. BULK UPLOAD EXCEL (Smart Logic) ---
@login_required(login_url='login')
def bulk_upload_marks(request):
    user = request.user
    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        class_id = request.POST.get('class_grade')
        excel_file = request.FILES.get('excel_file')

        if not (exam_id and class_id and excel_file):
            messages.error(request, "Please select Exam, Class and File.")
            return redirect('enter_marks')

        try:
            db_subjects = Subject.objects.filter(school=user.school, class_grade_id=class_id)
            subject_map = {sub.name.strip().lower(): sub for sub in db_subjects}

            df = pd.read_excel(excel_file, dtype={'Admission No': str})
            df.columns = df.columns.str.strip()

            count = 0
            for index, row in df.iterrows():
                adm_no = str(row.get('Admission No')).strip()
                student = Student.objects.filter(school=user.school, admission_no=adm_no).first()
                
                if student:
                    for col_name in df.columns:
                        clean_col = col_name.strip().lower()
                        if clean_col in subject_map:
                            subject = subject_map[clean_col]
                            marks_raw = row.get(col_name)
                            
                            if pd.notna(marks_raw) and str(marks_raw).strip() != '':
                                try:
                                    val = float(marks_raw)
                                    if val <= subject.total_marks:
                                        StudentResult.objects.update_or_create(
                                            school=user.school,
                                            exam_id=exam_id,
                                            subject=subject,
                                            student=student,
                                            defaults={'marks_obtained': val, 'total_marks': subject.total_marks}
                                        )
                                        count += 1
                                except: pass
            
            if count > 0: messages.success(request, f"✅ Processed {count} marks entries!")
            else: messages.warning(request, "No valid marks found.")

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return redirect('enter_marks')


# --- 4. RESULT LIST & REPORT CARD ---
@login_required(login_url='login')
def result_list(request):
    user = request.user
    exams = Exam.objects.filter(school=user.school)
    classes = ClassGrade.objects.filter(school=user.school)
    
    selected_exam_id = request.GET.get('exam')
    selected_class_id = request.GET.get('class_grade')
    
    students = []
    if selected_exam_id and selected_class_id:
        students = Student.objects.filter(school=user.school, current_class_id=selected_class_id, status='active').order_by('roll_number')

    return render(request, 'exams/result_list.html', {
        'exams': exams, 'classes': classes, 'students': students,
        'sel_exam': int(selected_exam_id) if selected_exam_id else None,
        'sel_class': int(selected_class_id) if selected_class_id else None
    })

@login_required(login_url='login')
def generate_report_card(request, student_id, exam_id):
    student = get_object_or_404(Student, pk=student_id, school=request.user.school)
    exam = get_object_or_404(Exam, pk=exam_id, school=request.user.school)
    results = StudentResult.objects.filter(student=student, exam=exam).select_related('subject')
    
    total_obtained = sum(res.marks_obtained for res in results)
    total_max = sum(res.subject.total_marks for res in results)
    percentage = round((total_obtained / total_max) * 100, 2) if total_max > 0 else 0
    
    grade = 'F'
    if percentage >= 90: grade = 'A+'
    elif percentage >= 80: grade = 'A'
    elif percentage >= 70: grade = 'B+'
    elif percentage >= 60: grade = 'B'
    elif percentage >= 50: grade = 'C'
    elif percentage >= 33: grade = 'D'

    return render(request, 'exams/report_card.html', {
        'student': student, 'exam': exam, 'results': results,
        'total_obtained': total_obtained, 'total_max': total_max,
        'percentage': percentage, 'grade': grade, 'status': "PASS" if grade != 'F' else "FAIL"
    })  