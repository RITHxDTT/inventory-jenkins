from common.views import catalog_views
from inventory.filters import SupplierFilter
from .models import Supplier
from .forms import SupplierForm
supplier_list, supplier_detail, supplier_edit, supplier_archive = catalog_views(Supplier, SupplierForm, SupplierFilter, 'suppliers')
