from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fields = ['affiliation', 'orcid', 'expertise_areas', 'bio', 'website']


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = BaseUserAdmin.list_display + ('get_affiliation',)
    
    def get_affiliation(self, obj):
        return obj.userprofile.affiliation if hasattr(obj, 'userprofile') else ''
    get_affiliation.short_description = 'Affiliation'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'affiliation', 'orcid', 'created_at']
    list_filter = ['created_at', 'affiliation']
    search_fields = ['user__username', 'user__email', 'affiliation', 'orcid']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
