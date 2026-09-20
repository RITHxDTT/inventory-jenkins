from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.db.models import Q
from common.views import page_context
from .models import AuditLog
@login_required
@permission_required('audit.view_auditlog', raise_exception=True)
def logs(request):
    qs = AuditLog.objects.select_related('user')
    q = request.GET.get('q', '')
    if q: qs = qs.filter(Q(action__icontains=q) | Q(description__icontains=q) | Q(user__username__icontains=q))
    return render(request, 'audit.html', dict(title='Audit log', **page_context(request, qs)))
