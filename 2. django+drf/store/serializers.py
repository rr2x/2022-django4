from decimal import Decimal
from venv import create
from store.models import Product, Collection, Review
from rest_framework import serializers


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    # read_only = True; because we don't need to edit it
    products_count = serializers.IntegerField(read_only=True)


# using model serializer
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory',
                  'unit_price', 'price_with_tax', 'collection']

    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']

    # override, because we are not retrieving product
    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)


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
