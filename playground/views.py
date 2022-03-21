from django.shortcuts import render
# Q = query expression
# F = field expression
from django.db.models import Q, F
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from store.models import Product, OrderItem


def say_hello2(request):
    # return queryset and not the actual product
    products = Product.objects.all()

    # when we loop, this evaluates the queryset and executes sql to database
    for product in products:
        print(product)

    # other queryset evaluation:
    #   when we convert to list
    #   when we slice or slice
    # queryset are lazy, or evaluated at a later time

    return render(request, 'hello.html', {'name': 'fox'})


def say_hello3(request):
    # get product object, if does not exist throw error
    # product = Product.objects.get(pk=0)

    # filter product object and then get 1st occurance, if does not exist return None
    # product = Product.objects.filter(pk=0).first()

    # check if certain product exists, return boolean
    # product_exists = Product.objects.filter(pk=0).exists()

    # __## = lookup type
    # __gt = greater than
    # queryset = Product.objects.filter(unit_price__gt=20)

    # __range = range, need to pass a tuple of minimum and maximum
    # queryset = Product.objects.filter(unit_price__range=(20, 30))

    # case insensitive lookup for "contains"
    # queryset = Product.objects.filter(title__icontains='coffee')

    # queryset = Product.objects.filter(last_update__year=2021)
    queryset = Product.objects.filter(description__isnull=True)

    return render(request, 'hello.html', {'name': 'fox', 'products': list(queryset)})


def say_hello4(request):
    # products: inventory < 10 and price < 20
    # queryset = Product.objects.filter(inventory__lt=10, unit_price__lt=20)
    # alternative:
    # queryset = Product.objects.filter(inventory__lt=10).filter(unit_price__lt=20)

    # logical OR, if you want AND just pass all queries without Q object
    # queryset = Product.objects.filter(Q(inventory__lt=10) | Q(unit_price__lt=20))

    # negation (~) translated to NOT operator
    queryset = Product.objects.filter(
        Q(inventory__lt=10) & ~Q(unit_price__lt=20))

    return render(request, 'hello.html', {'name': 'fox', 'products': list(queryset)})


def say_hello5(request):
    # queryset = Product.objects.filter(inventory=F('collection__id'))
    queryset = Product.objects.filter(inventory=F('unit_price'))

    return render(request, 'hello.html', {'name': 'fox', 'products': list(queryset)})


def say_hello6(request):
    # sort title in ascending order
    # queryset = Product.objects.order_by('title')

    # order by unit_price, then sort title in descending order.. then reverse direction of sort
    # queryset = Product.objects.order_by('unit_price', '-title').reverse()

    # sort result by unit_price and get the 1st object.. alternative = latest (descending)
    # this does not evaluate, compared to equivalent:  .order_by('...')[#]
    queryset = Product.objects.earliest('unit_price')

    return render(request, 'hello.html', {'name': 'fox', 'products': list(queryset)})


def say_hello7(request):
    # get objects 0 to 4
    # queryset = Product.objects.all()[:5]

    # get objects 5 to 9
    # skip first 5 (offset 5)
    queryset = Product.objects.all()[5:10]

    return render(request, 'hello.html', {'name': 'fox', 'products': list(queryset)})


def say_hello(request):
    # only limit to specific columns, and include related field from another table
    # .values()  will return a dictionary of objects
    # queryset = Product.objects.values('id', 'title', 'collection__title')

    # .values_list() will return a list of tuple objects
    # queryset = Product.objects.values('id', 'title', 'collection__title')

    # --- select products that have been 'ordered' and sort them by title
    # .disctinct() = method of queryset object to remove duplicates
    # id__in = get id within range
    queryset = Product.objects.filter(id__in=OrderItem.objects.values(
        'product_id').distinct()).order_by('title')

    return render(request, 'hello2.html', {'name': 'fox', 'products': list(queryset)})
