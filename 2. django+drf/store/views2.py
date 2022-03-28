from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models.aggregates import Count
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from .models import Product, Collection
from .serializers import ProductSerializer, CollectionSerializer


# ---- old views.py ----


@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        # select_related = preload collection table so that
        # it bypasses lazy loading and prevent too much queries
        queryset = Product.objects.select_related('collection').all()
        # many=True cycle through all data
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        # deserialize data
        serializer = ProductSerializer(data=request.data)
        # raise_exception=True, automatically return http 400 bad request if error
        # for less code
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, id):
    # try:
    #     product = Product.objects.get(pk=id)
    #     serializer = ProductSerializer(product)
    #     return Response(serializer.data)
    # except Product.DoesNotExist:
    #     return Response(status=status.HTTP_404_NOT_FOUND)

    # get_object_or_404() wraps the try-catch block above
    product = get_object_or_404(Product, pk=id)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if product.orderitems.count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def collection_list(request):
    if request.method == 'GET':
        queryset = Collection.objects.annotate(
            products_count=Count('product_x')).all()
        serializer = CollectionSerializer(queryset, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def collection_detail(request, pk):
    collection = get_object_or_404(Collection.objects.annotate(
        products_count=Count('product_x')), pk=pk)

    if request.method == 'GET':
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    elif request.method == 'DELETE':
        if collection.product_x.count() > 0:
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
