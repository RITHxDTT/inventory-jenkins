from .models import AuditLog


def log_action(user, action, obj, description=''):
    return AuditLog.objects.create(user=user, action=action, object_type=obj._meta.label, object_id=str(obj.pk),
                                   description=description or str(obj))
