from decimal import Decimal
from store.models import Cart, CartItem, Product, Collection, Review
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


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    # get product objects instead of id
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        # total_price = calculated field
        fields = ['id', 'product', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    # get cartitem objects instead of id, read_only so that you don't edit it
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart: Cart):
        # list comprehension
        return sum([x.quantity * x.product.unit_price for x in cart.items.all()])

    class Meta:
        model = Cart
        # items = reverse relationship name from cartitem table
        # total_price = calculated field
        fields = ['id', 'items', 'total_price']


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
