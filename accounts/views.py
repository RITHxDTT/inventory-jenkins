from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from common.views import page_context
from audit.services import log_action
from inventory.filters import UserFilter
from .forms import UserCreateForm, UserEditForm, ProfileForm, ImageForm, GroupForm
from .models import Profile
@login_required
@permission_required('auth.view_user', raise_exception=True)
def users(request):
    f = UserFilter(request.GET, queryset=User.objects.prefetch_related('groups').order_by('username'))
    return render(request, 'users.html', dict(title='Users', filter=f, **page_context(request, f.qs)))
@login_required
def user_edit(request, pk=None):
    from django.core.exceptions import PermissionDenied
    if not request.user.has_perm('auth.change_user' if pk else 'auth.add_user'):
        raise PermissionDenied
    obj = get_object_or_404(User, pk=pk) if pk else None
    if obj and obj.is_superuser and not request.user.is_superuser:
        raise PermissionDenied
    form = (UserEditForm if pk else UserCreateForm)(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        if obj and obj.pk == request.user.pk and not form.cleaned_data['is_active']:
            form.add_error('is_active', 'You cannot deactivate your own account.')
        else:
            with transaction.atomic():
                obj = form.save()
                log_action(request.user, 'User updated' if pk else 'User created', obj, f'{obj.username}; active={obj.is_active}')
            messages.success(request, 'User saved successfully.')
            return redirect('users')
    return render(request, 'form.html', {'title': 'Edit user' if pk else 'Create user', 'form': form, 'cancel_url': 'users'})
@login_required
def profile(request):
    obj, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=request.user)
    image_form = ImageForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid() and image_form.is_valid():
        with transaction.atomic():
            form.save(); image_form.save()
            log_action(request.user, 'Profile updated', request.user)
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    return render(request, 'profile.html', {'title': 'My profile', 'form': form, 'image_form': image_form, 'profile': obj})
@login_required
@permission_required('auth.view_group', raise_exception=True)
def roles(request):
    return render(request, 'roles.html', {'title': 'Roles & permissions', 'groups': Group.objects.prefetch_related('permissions')})
@login_required
def role_edit(request, pk=None):
    from django.core.exceptions import PermissionDenied
    if not request.user.has_perm('auth.change_group' if pk else 'auth.add_group'): raise PermissionDenied
    obj = get_object_or_404(Group, pk=pk) if pk else None
    form = GroupForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            obj = form.save()
            log_action(request.user, 'Role updated' if pk else 'Role created', obj)
        messages.success(request, 'Role saved successfully.')
        return redirect('roles')
    return render(request, 'form.html', {'title': 'Edit role' if pk else 'Create role', 'form': form, 'cancel_url': 'roles'})
