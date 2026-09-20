from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from audit.services import log_action

def page_context(request, queryset):
    query = request.GET.copy()
    query.pop('page', None)
    return {'page_obj': Paginator(queryset, 15).get_page(request.GET.get('page')), 'querystring': query.urlencode()}

def catalog_views(model, form_class, filter_class, slug):
    app = model._meta.app_label
    name = model._meta.model_name
    def protect(action):
        return lambda view: login_required(permission_required(f'{app}.{action}_{name}', raise_exception=True)(view))
    @protect('view')
    def listing(request):
        qs = model.objects.all()
        if name == 'product': qs = qs.select_related('category', 'supplier')
        f = filter_class(request.GET, queryset=qs)
        return render(request, 'catalog_list.html', dict(title=model._meta.verbose_name_plural.title(), kind=name, slug=slug, filter=f, can_add=request.user.has_perm(f'{app}.add_{name}'), **page_context(request, f.qs)))
    @protect('view')
    def detail(request, pk):
        obj = get_object_or_404(model, pk=pk)
        fields = [(field.verbose_name, getattr(obj, field.name)) for field in model._meta.fields if field.name not in ['id', 'image']]
        return render(request, 'detail.html', {'title': str(obj), 'object': obj, 'fields': fields, 'slug': slug, 'kind': name, 'can_change': request.user.has_perm(f'{app}.change_{name}'), 'can_archive': request.user.has_perm(f'{app}.delete_{name}'), 'products': obj.products.all()[:30] if hasattr(obj, 'products') else None, 'transactions': obj.transactions.select_related('performed_by')[:10] if name == 'product' and request.user.has_perm('inventory.view_stocktransaction') else None})
    def edit(request, pk=None):
        needed = f'{app}.change_{name}' if pk else f'{app}.add_{name}'
        if not request.user.has_perm(needed):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        obj = get_object_or_404(model, pk=pk) if pk else None
        form = form_class(request.POST or None, request.FILES or None, instance=obj)
        if request.method == 'POST' and form.is_valid():
            with transaction.atomic():
                obj = form.save()
                log_action(request.user, 'Updated' if pk else 'Created', obj)
            messages.success(request, f'{model._meta.verbose_name.title()} saved successfully.')
            return redirect(f'{slug}-detail', pk=obj.pk)
        return render(request, 'form.html', {'title': ('Edit ' if pk else 'Create ') + model._meta.verbose_name, 'form': form, 'cancel_url': f'{slug}-list'})
    @protect('delete')
    def archive(request, pk):
        obj = get_object_or_404(model, pk=pk)
        if request.method == 'POST':
            with transaction.atomic():
                obj = model.objects.select_for_update().get(pk=pk)
                obj.is_active = False
                obj.save(update_fields=['is_active', 'updated_at'])
                log_action(request.user, 'Archived', obj)
            messages.success(request, f'{obj} archived. Historical records are preserved.')
            return redirect(f'{slug}-list')
        return render(request, 'confirm.html', {'title': 'Archive ' + str(obj), 'description': 'This record will become inactive. Its history and relationships will be preserved.', 'cancel_url': f'{slug}-list'})
    return listing, detail, login_required(edit), archive
