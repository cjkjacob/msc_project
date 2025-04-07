from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

ROLE_CHOICES = [
    ('student', 'Student'),
    ('validator', 'Validator'),
    ('admin', 'Admin')
]

class UserWallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)    
    public_key = models.TextField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class TokenLedger(models.Model):
    user = models.ForeignKey(UserWallet, on_delete=models.CASCADE, related_name="transactions")
    amount = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    source_block_index = models.IntegerField()
    reason = models.CharField(max_length=255, default="Effort reward")

    def __str__(self):
        return f"{self.user.user.username} earned {self.amount} EFF (block #{self.source_block_index})"
    
class PendingEffort(models.Model):
    effort_data = models.JSONField()
    user_signature = models.TextField()
    user_public_key = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    submitted_by = models.CharField(max_length=100)
    assigned_validator = models.CharField(max_length=100, blank=True, null=True)
    is_expired = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Pending: {self.effort_data.get('task_id')} by {self.submitted_by}"
    
class PendingEffortAdmin(admin.ModelAdmin):
    list_display = ('submitted_by', 'task_id', 'uploaded_file', 'is_expired')
    readonly_fields = ('uploaded_file',)

    def task_id(self, obj):
        return obj.effort_data.get('task_id', 'N/A')

    def uploaded_file(self, obj):
        url = obj.effort_data.get('submission', {}).get('file_url')
        if url:
            return mark_safe(f"<a href='{url}' target='_blank'>📎 View File</a>")
        return "No file"



admin.site.register(UserWallet)
admin.site.register(TokenLedger)
admin.site.register(PendingEffort, PendingEffortAdmin)
