from decimal import Decimal
from store.models import Product, Collection
from rest_framework import serializers


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title']


# using model serializer
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price', 'price_with_tax', 'collection']

    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)


# class CollectionSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField()

# class ProductSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
#     # source = lookup on data model for this column
#     price = serializers.DecimalField(
#         max_digits=6, decimal_places=2, source='unit_price')
#     # custom serializer field
#     price_with_tax = serializers.SerializerMethodField(
#         method_name='calculate_tax')

#     # show ids
#     # collection = serializers.PrimaryKeyRelatedField(
#     #     queryset=Collection.objects.all()
#     # )

#     # show __str__ value of collection object
#     # collection = serializers.StringRelatedField()

#     # show nested object
#     collection = CollectionSerializer()

#     def calculate_tax(self, product: Product):
#         return product.unit_price * Decimal(1.1)
