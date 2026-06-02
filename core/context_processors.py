def institute_labels(request):
    # Default Labels (School)
    labels = {
        'TYPE': 'School',
        'L_STUDENT': 'Student',
        'L_NAME': 'Student Name',
        'L_FATHER': "Father's Name",
        'L_CLASS': 'Class',
        'L_SECTION': 'Section',
        'L_ROLL': 'Roll Number',
        'L_ADMISSION_NO': 'Admission No',
        'L_FEES': 'Fees',
        'L_PRINCIPAL': 'Principal',
    }

    if request.user.is_authenticated and hasattr(request.user, 'school') and request.user.school:
        try:
            itype = request.user.school.institute_type

            # 🕋 MADRASA MODE
            if itype == 'madrasa':
                labels = {
                    'TYPE': 'Madrasa',
                    'L_STUDENT': 'Talib-e-Ilm',
                    'L_NAME': 'Talib Ka Naam',
                    'L_FATHER': 'Walid Ka Naam',
                    'L_CLASS': 'Darja (Class)',
                    'L_SECTION': 'Jamaat',
                    'L_ROLL': 'Reg. Number',
                    'L_ADMISSION_NO': 'Dakhila Number',
                    'L_FEES': 'Chanda / Fees',
                    'L_PRINCIPAL': 'Nazim Sahab',
                }
            
            # 🎓 COACHING MODE
            elif itype == 'coaching':
                labels = {
                    'TYPE': 'Institute',
                    'L_STUDENT': 'Aspirant',
                    'L_NAME': 'Student Name',
                    'L_FATHER': "Guardian's Name",
                    'L_CLASS': 'Batch',
                    'L_SECTION': 'Time Slot',
                    'L_ROLL': 'ID Number',
                    'L_ADMISSION_NO': 'Registration No',
                    'L_FEES': 'Course Fee',
                    'L_PRINCIPAL': 'Director',
                }
        except Exception:
            pass 

    return labels