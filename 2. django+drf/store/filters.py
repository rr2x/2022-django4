from django_filters.rest_framework import FilterSet
from .models import Product


class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            # equality comparison
            'collection_id': ['exact'],
            # less than or greater than
            'unit_price': ['gt', 'lt']
        }
