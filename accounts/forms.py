from django import forms
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.forms import UserCreationForm
from common.forms import StyledFormMixin
from .models import Profile


class UserCreateForm(StyledFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['username', 'first_name', 'last_name', 'email', 'groups', 'user_permissions', 'is_active']


class UserEditForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'groups', 'user_permissions', 'is_active']


class ProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ImageForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']


class GroupForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'permissions']
