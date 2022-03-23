from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
# Q = query expression
# F = field expression
from django.db.models import Q, F, Value, Func, ExpressionWrapper, DecimalField
from django.db.models.functions import Concat
from django.db.models.aggregates import Count, Max, Min, Avg, Sum
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from store.models import Product, OrderItem, Order, Customer
from tags.models import TaggedItem


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


def say_hello8(request):
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


def say_hello9(request):
    # deferring fields
    # .values() = dictionary of objects

    # .only() = instances of objects
    # careful when using this because you will have alot of queries executed
    # queryset = Product.objects.only('id', 'title')

    # defer certain fields later
    # interested in all columns except 'description'
    queryset = Product.objects.defer('description')

    return render(request, 'hello2.html', {'name': 'fox', 'products': list(queryset)})


def say_hello10(request):
    # preload 'collection'
    # create join between tables
    # select_related (1 instance) for ForeignKey
    #queryset = Product.objects.select_related('collection').all()

    # prefetch_related (many instance) for ManyToManyField
    # queryset = Product.objects.prefetch_related('promotions').all()

    # combine
    queryset = Product.objects.prefetch_related(
        'promotions').select_related('collection').all()

    return render(request, 'hello2.html', {'name': 'fox', 'products': list(queryset)})


def say_hello11(request):
    # q: get the last 5 orders with their customer and items (including product):

    # 1. preload 'customer' field from 'orders' table
    # 2. preload items of these orders, 'orderitem_set' is generated by django as name of reverse relationship
    # 3. load related product referenced in each orderitem 'orderitem_set__product'
    # 4. sort by 'placed_at' in decending order so latest orders comes first
    # 5. array slicing syntax [:5] to pick top 5

    queryset = Order.objects.select_related(
        'customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5]

    return render(request, 'hello3.html', {'name': 'fox', 'orders': list(queryset)})


def say_hello12(request):
    # compute totals (aggregation), does not return queryset

    # count number of records, return dictionary
    result = Product.objects.aggregate(
        count=Count('id'), min_price=Min('unit_price'))

    # result = Product.objects.filter(collection__id=1).aggregate(
    #     count=Count('id'), min_price=Min('unit_price'))

    return render(request, 'hello4.html', {'name': 'fox', 'result': result})


def say_hello13(request):
    # annotating objects, its like adding a new column on queryset

    # queryset = Customer.objects.annotate(is_new=Value(True))
    # queryset = Customer.objects.annotate(new_id=F('id')+1)

    # Func = sql function call
    # computed column
    # queryset = Customer.objects.annotate(
    #     # function='CONCAT', map to function named CONCAT
    #     full_name=Func(F('first_name'), Value(' '), F('last_name'), function='CONCAT')
    # )

    # shortcut
    queryset = Customer.objects.annotate(
        # function='CONCAT', map to function named CONCAT
        full_name=Concat('first_name', Value(' '), 'last_name'))

    # can check more db functions here: https://docs.djangoproject.com/en/4.0/ref/models/database-functions/

    return render(request, 'hello4.html', {'name': 'fox', 'result': list(queryset)})


def say_hello14(request):
    # left outer join, because not every customer has an order
    queryset = Customer.objects.annotate(
        # name that needs to be used is "order" instead of "order_set"
        orders_count=Count('order')
    )

    return render(request, 'hello4.html', {'name': 'fox', 'result': list(queryset)})


def say_hello15(request):
    # FloatField() has rounding issues
    discounted_price = ExpressionWrapper(
        F('unit_price') * 0.8, output_field=DecimalField())

    queryset = Product.objects.annotate(
        discounted_price=discounted_price
    )

    return render(request, 'hello4.html', {'name': 'fox', 'result': list(queryset)})


def say_hello(request):
    # querying generic relationships
    # using django_content_type table

    content_type = ContentType.objects.get_for_model(Product)

    # preload tag, use \ to go next line
    queryset = TaggedItem.objects \
        .select_related('tag') \
        .filter(
            content_type=content_type,
            object_id=1
        )

    return render(request, 'hello5.html', {'name': 'fox', 'tags': list(queryset)})
