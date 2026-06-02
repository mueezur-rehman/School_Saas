import os
import django

# 🚀 Django settings ko initialize karna zaroori hai standalone script ke liye
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_saas.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_default_admin():
    User = get_user_model()
    
    # 🔐 APNE HISAAB SE ID / PASSWORD SET KAREIN
    ADMIN_EMAIL = "admin@leadsbytech.com"
    ADMIN_PASSWORD = "SecureAdminPassword2026"
    
    print("⏳ Checking for Super Admin existence...")
    
    # Check ki kya ye admin pehle se database mein hai
    if not User.objects.filter(email=ADMIN_EMAIL).exists():
        print(f"✨ Creating new Super Admin: {ADMIN_EMAIL}")
        
        # Base superuser create karna
        superuser = User.objects.create_superuser(
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD,
        )
        
        # Agar aapke CustomUser model mein 'role' ya koi aur extra fields hain, 
        # toh unhe yahan safely update kiya ja sakta hai
        if hasattr(superuser, 'role'):
            superuser.role = 'super_admin'
        
        if hasattr(superuser, 'first_name'):
            superuser.first_name = "Mueezur"
        if hasattr(superuser, 'last_name'):
            superuser.last_name = "Rehman"
            
        superuser.save()
        print("✅ Super Admin created successfully!")
        print(f"📧 Email: {ADMIN_EMAIL}")
        print(f"🔑 Password: {ADMIN_PASSWORD}")
        print("⚠️ Pro-Tip: Security ke liye live server par login karne ke baad password turant badal lena!")
    else:
        print(f"ℹ️ Super Admin with email '{ADMIN_EMAIL}' already exists. Skipping creation.")

if __name__ == "__main__":
    create_default_admin()