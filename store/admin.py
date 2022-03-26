from django.contrib import admin, messages
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low')  # ("value", "visible on page")
        ]

    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    actions = ['clear_inventory']

    # https://docs.djangoproject.com/en/4.0/ref/contrib/admin/#modeladmin-options
    list_display = ['title', 'unit_price',
                    'inventory', 'inventory_status', 'collection_title']
    list_editable = ['unit_price', 'inventory']
    # enable sidebar filtering
    list_filter = ['collection', 'last_update', InventoryFilter]
    list_per_page = 10
    # eager load related object from collection to reduce sql queries
    list_select_related = ['collection']

    def collection_title(self, product):
        return product.collection.title

    # computed column, does not exist from Product table
    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:  # check 'inventory' column
            return 'Low'
        return 'OK'

    # custom action
    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        # show message
        self.message_user(
            request,
            f'{updated_count} product(s) were successfully updated',
            messages.ERROR
        )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'orders']
    list_editable = ['membership']
    list_per_page = 10
    ordering = ['first_name', 'last_name']
    # case insensitive startswith searching option
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    @admin.display(ordering='orders')
    def orders(self, customer):
        url = (
            reverse('admin:store_order_changelist')
            + '?'
            + urlencode({
                'customer__id': str(customer.id)
            }))
        return format_html('<a href="{}">{}</a>', url, customer.orders)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders=Count('order')
        )


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'placed_at', 'customer', 'payment_status']
    list_editable = ['payment_status']
    list_select_related = ['customer']
    list_per_page = 10


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']

    # 'products_count' does not really exist from Collection table
    @admin.display(ordering='products_count')
    def products_count(self, collection):
        # <app>_<model>_<page>
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({
                'collection__id': str(collection.id)
            }))
        return format_html('<a href="{}">{}</a>', url, collection.products_count)

    # override queryset, annotate with 'products_count'
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('product')
        )
