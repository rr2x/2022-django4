from django.db.models.aggregates import Count
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin

from store.permissions import FullDjangoModelPermissions, IsAdminOrReadOnly, ViewCustomerHistoryPermission

from .filters import ProductFilter
from .pagination import DefaultPagination
from .models import Cart, CartItem, Customer, Order, OrderItem, Product, Collection, Review, ProductImage
from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CreateOrderSerializer, CustomerSerializer, OrderSerializer, ProductImageSerializer, ProductSerializer, CollectionSerializer, ReviewSerializer, UpdateCartItemSerializer, UpdateOrderSerializer


from django.contrib.auth.models import Permission


# @api_view -> APIView -> GenericView -> ModelViewSet

# ViewSet = set of related views, combining multiple generic views into one

# combined ProductList and ProductDetail generic views
class ProductViewSet(ModelViewSet):
    # eager load products with their images
    queryset = Product.objects.prefetch_related('images').all()
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter,
                       filters.DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductFilter
    # pagination_class = PageNumberPagination
    pagination_class = DefaultPagination
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']
    # limit full acccess to admin only
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an OrderItem.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    # let serializer retrieve the product_id from url
    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])


# combined CollectionList and CollectionDetail generic views
class CollectionViewSet(ModelViewSet):
    # annotate lets you add objects on queryset
    queryset = Collection.objects.annotate(
        products_count=Count('product_x')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Collection cannot be deleted because it includes one or more Product.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    # override queryset so you only retrieve review related to a product
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    # override because we want to retrieve product id from url
    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


# instead of inheriting ModelViewSet,
# we just inherit mixins (which builds a ModelViewSet)
# because we don't use all CRUD operations here
class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    # because carts can have multiple items, so eager load them for performance
    # if foreign keys with single related object, use select_related()
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    # allowable methods, we don't need PUT request
    # method names needs to be in lowercase
    http_method_names = ['get', 'post', 'patch', 'delete']

    # pass cart_id from view to serializer
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    # return serializer depending on request method
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_queryset(self):
        return CartItem.objects \
            .select_related('product') \
            .filter(cart_id=self.kwargs['cart_pk'])


# we need specific functionality, we should not list customers in normal views
class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    # DjangoModelPermissions, depending on group permissions defined by django
    # if group permission of user does not have access then deny them
    # permission_classes = [FullDjangoModelPermissions]

    # for this app, just allow admin
    permission_classes = [IsAdminUser]

    # detail=True; particular customer
    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):
        return Response('ok')

    # override permission class depending on method
    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [AllowAny()]
    #     # if method is not get request, then permission IsAuthenticated() is returned
    #     return [IsAuthenticated()]

    # override, for non admin
    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        # unpack tuple from .get_or_create()
        # (customer, created) = Customer.objects.get_or_create(user_id=request.user.id)

        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data=request.data,
            context={'user_id': self.request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    # def get_serializer_context(self):
    #     return {'user_id': self.request.user.id}

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()

        # # fix, don't use get_or_create... needs separation of queries,
        # # should not create a new profile when just getting order
        # # command query separation principle, never change the state of the system on get
        # (customer_id, created) = Customer.objects.only(
        #     'id').get_or_create(user_id=user.id)

        # fixed problem above using django signals
        customer_id = Customer.objects.only('id').get(user_id=user.id)

        return Order.objects.filter(customer_id=customer_id)


# region "old code"

# APIView: simplify endpoint development

# class ProductList(APIView):
#     def get(self, request):
#         queryset = Product.objects.select_related('collection').all()
#         serializer = ProductSerializer(queryset, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

# class ProductDetail(APIView):
#     def get(self, request, id):
#         product = get_object_or_404(Product, pk=id)
#         serializer = ProductSerializer(product)
#         return Response(serializer.data)

#     def put(self, request, id):
#         product = get_object_or_404(Product, pk=id)
#         serializer = ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

#     def delete(self, request, id):
#         product = get_object_or_404(Product, pk=id)
#         if product.orderitems.count() > 0:
#             return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# Mixins: encapsulate repeating patterns seen on APIView for code reuse
# Generic Views: uses one or more Mixins

# genericview usage
# class ProductList(ListCreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     # only useful if you need logic during queryset use
#     # def get_queryset(self):
#     #     return Product.objects.select_related('collection').all()

#     # only useful if you need logic for a different serializer
#     # def get_serializer_class(self):
#     #     return ProductSerializer

#     def get_serializer_context(self):
#         return {'request': self.request}


# class ProductDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     # override implementation because of custom code that does not exist on mixin
#     def delete(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.orderitems.count() > 0:
#             return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class CollectionList(ListCreateAPIView):
#     queryset = Collection.objects.annotate(
#         products_count=Count('product_x')).all()
#     serializer_class = CollectionSerializer

# class CollectionDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Collection.objects.annotate(
#         products_count=Count('product_x')).all()
#     serializer_class = CollectionSerializer

#     def delete(self, request, pk):
#         collection = get_object_or_404(Collection, pk=pk)
#         if collection.product_x.count() > 0:
#             return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# endregion
