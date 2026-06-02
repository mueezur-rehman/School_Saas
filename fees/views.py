from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from students.models import Student
from core.models import AcademicSession
from .models import FeeStructure, FeePayment
from academics.models import ClassGrade
from urllib.parse import quote

# --- HELPER: CURRENT SESSION ---
def get_current_session(school):
    return AcademicSession.objects.filter(school=school, is_current=True).first()

# 1. FEES COLLECT VIEW
@login_required(login_url='login')
def collect_fees(request):
    user = request.user
    if not user.school:
        return render(request, 'core/error.html', {'message': "Restricted Access"})

    # A. Session Check
    current_session = get_current_session(user.school)
    if not current_session:
        return render(request, 'core/error.html', {
            'message': "⚠️ No Active Academic Session Found! Please go to Admin Panel > Core > Academic Sessions and create a session (e.g., 2025-26)."
        })

    student = None
    fee_structures = []
    total_fee = 0
    total_paid = 0
    balance = 0
    
    # URL se admission number lena
    search_adm_no = request.GET.get('admission_no')

    if search_adm_no:
        try:
            # 🔍 SEARCH LOGIC
            student = Student.objects.get(admission_no=search_adm_no, school=user.school)
            
            # 🧮 CALCULATION LOGIC
            # 1. Total Fee (Structure se)
            structures = FeeStructure.objects.filter(class_grade=student.current_class, school=user.school)
            fee_structures = structures
            total_fee_data = structures.aggregate(Sum('amount'))
            total_fee = total_fee_data['amount__sum'] or 0

            # 2. Total Paid (Sirf Current Session ka)
            paid_data = FeePayment.objects.filter(
                student=student, 
                session=current_session
            ).aggregate(Sum('amount_paid'))
            
            total_paid = paid_data['amount_paid__sum'] or 0

            # 3. Balance
            balance = total_fee - total_paid

        except Student.DoesNotExist:
            messages.error(request, "Student not found with this Admission Number!")

    # 💸 PAYMENT LOGIC
    if request.method == 'POST' and student:
        try:
            amount = float(request.POST.get('amount'))
            mode = request.POST.get('mode')
            remarks = request.POST.get('remarks')
            
            if amount > 0:
                # Payment Record Save (With Session)
                payment = FeePayment.objects.create(
                    school=user.school,
                    student=student,
                    session=current_session,
                    amount_paid=amount,
                    mode=mode,
                    remarks=remarks
                )
                
                messages.success(request, f"Success! ₹{amount} collected in session {current_session.name}.")
                return redirect('payment_receipt', pk=payment.pk)
                
        except ValueError:
            messages.error(request, "Invalid Amount Entered!")

    context = {
        'student': student,
        'fee_structures': fee_structures,
        'total_fee': total_fee,
        'total_paid': total_paid,
        'balance': balance,
        'search_adm_no': search_adm_no,
        'current_session': current_session
    }
    return render(request, 'fees/collect_fees.html', context)


# 2. RECEIPT VIEW
@login_required(login_url='login')
def payment_receipt(request, pk):
    payment = get_object_or_404(FeePayment, pk=pk, school=request.user.school)
    
    # --- 📲 WHATSAPP LOGIC ---
    student = payment.student
    school_name = payment.school.name
    
    # Message Format
    message = (
        f"✅ Fees Received!\n\n"
        f"Dear Parent,\n"
        f"We have received ₹{payment.amount_paid} for {student.first_name} {student.last_name}.\n"
        f"Receipt No: #{payment.id}\n"
        f"Session: {payment.session.name if payment.session else 'N/A'}\n"
        f"Date: {payment.payment_date}\n\n"
        f"Thank you,\n"
        f"*{school_name}*"
    )
    
    # URL Encode
    encoded_message = quote(message)
    
    # Mobile Number Cleaning
    raw_mobile = str(student.father_mobile).strip()
    clean_mobile = ''.join(filter(str.isdigit, raw_mobile))
    
    if len(clean_mobile) == 10:
        clean_mobile = "91" + clean_mobile
    
    whatsapp_url = f"https://wa.me/{clean_mobile}?text={encoded_message}"

    return render(request, 'fees/receipt.html', {
        'payment': payment,
        'whatsapp_url': whatsapp_url
    })

# 3. DEFAULTER LIST VIEW (NEW FUNCTION)
@login_required(login_url='login')
def defaulter_list(request):
    user = request.user
    if not user.school:
        return render(request, 'core/error.html', {'message': "Restricted Access"})

    # 1. Active Session Check
    current_session = get_current_session(user.school)
    if not current_session:
        return render(request, 'core/error.html', {'message': "No Active Session Found!"})

    # 2. Filtering (Class Wise)
    class_id = request.GET.get('class_grade')
    classes = ClassGrade.objects.filter(school=user.school)
    
    students = Student.objects.filter(
        school=user.school, 
        session=current_session, 
        status='active'
    ).select_related('current_class', 'section')

    if class_id:
        students = students.filter(current_class_id=class_id)

    defaulters = []
    total_due_amount = 0

    # 3. Calculation Loop
    for student in students:
        # A. Total Fees for this Class
        structures = FeeStructure.objects.filter(class_grade=student.current_class, school=user.school)
        total_payable = structures.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # B. Total Paid in this Session
        paid_data = FeePayment.objects.filter(
            student=student, 
            session=current_session
        ).aggregate(Sum('amount_paid'))
        total_paid = paid_data['amount_paid__sum'] or 0
        
        # C. Balance
        balance = total_payable - total_paid
        
        # D. Agar Udhari hai (>0), to list me daalo
        if balance > 0:
            # WhatsApp Reminder Link
            msg = f"Dear Parent, Fees due for {student.first_name}: ₹{balance}. Please pay immediately. - {user.school.name}"
            
            # Clean Mobile Number
            mobile = str(student.father_mobile).strip()
            clean_mobile = ''.join(filter(str.isdigit, mobile))
            if len(clean_mobile) == 10: clean_mobile = "91" + clean_mobile
            
            wa_link = f"https://wa.me/{clean_mobile}?text={quote(msg)}"

            defaulters.append({
                'student': student,
                'total': total_payable,
                'paid': total_paid,
                'due': balance,
                'wa_link': wa_link
            })
            total_due_amount += balance

    context = {
        'defaulters': defaulters,
        'classes': classes,
        'selected_class': int(class_id) if class_id else None,
        'total_due': total_due_amount,
        'current_session': current_session
    }
    return render(request, 'fees/defaulter_list.html', context)