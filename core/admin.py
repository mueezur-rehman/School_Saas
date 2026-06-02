from django.contrib import admin
from .models import School, AcademicSession

# 👇 Security Guard (Mixin) - Jo humne pehle banaya tha
class SchoolAccessMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(school=request.user.school)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.school = request.user.school
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if hasattr(db_field.related_model, 'school'):
                kwargs["queryset"] = db_field.related_model.objects.filter(school=request.user.school)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_exclude(self, request, obj=None):
        if not request.user.is_superuser:
            return ('school',)
        return []

# 👇 SCHOOL ADMIN (Sirf Superuser ke liye)
@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'subscription_end_date')

# 👇 YEH RAHA WO MISSING SESSION ADMIN
@admin.register(AcademicSession)
class AcademicSessionAdmin(SchoolAccessMixin, admin.ModelAdmin):
    list_display = ('name', 'is_current', 'start_date', 'end_date')
    list_filter = ('is_current',)
    list_editable = ('is_current',) # Bahar se hi Tick/Untick kar sako
    ordering = ('-start_date',)