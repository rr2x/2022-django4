from webbrowser import get
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.mail import send_mail, mail_admins, BadHeaderError, EmailMessage
from templated_mail.mail import BaseEmailMessage
from django.db import transaction, connection
# Q = query expression
# F = field expression
from django.db.models import Q, F, Value, Func, ExpressionWrapper, DecimalField
from django.db.models.functions import Concat
from django.db.models.aggregates import Count, Max, Min, Avg, Sum
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from store.models import Product, OrderItem, Order, Customer, Collection
from tags.models import TaggedItem
from .tasks import notify_customers

from rest_framework.views import APIView
import requests
import logging


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
    # .values()  will return a dictionary of objects:       {'id':'', 'title':'' ,'collection__title':''}
    # queryset = Product.objects.values('id', 'title', 'collection__title')

    # .values_list() will return a list of tuple objects:   [('id',''), ('title',''), ('collection__title','')]
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


def say_hello16(request):
    queryset = TaggedItem.objects.get_tags_for(Product, 1)
    return render(request, 'hello5.html', {'name': 'fox', 'tags': list(queryset)})


def say_hello17(request):
    # queryset cache = memory used after 1st execution of query
    # only happens after evaluating a queryset
    # if you access a specific index on a queryset and then evaluate as list,
    # ... it will have multiple calls to database compared to evaluate then specific index

    queryset = Product.objects.all()
    return render(request, 'hello5.html', {'name': 'fox', 'tags': list(queryset)})


def say_hello18(request):
    # -- creating objects --
    # not using initialization kwargs because F2 will not update the properties
    collection = Collection()
    collection.title = "Video Games"
    collection.featured_product = Product(pk=1)
    # or collection.featured_product_id = 1
    collection.save()

    # shorthand:
    collection = Collection.objects.create(title="a", featured_product_id=1)

    return render(request, 'hello5.html', {'name': 'fox', 'tags': list(None)})


def say_hello19(request):
    # -- updating objects --

    # IMPORTANT: read objects first before updating it to prevent data loss
    # ... however it has performance problem
    collection = Collection.objects.get(pk=11)
    collection.title = "yo mama"
    collection.featured_product = None
    collection.save()

    # optimized code: update data in the database without data loss
    Collection.objects.filter(pk=11).update(
        featured_product=Product(pk=4), title="was fat")

    return render(request, 'hello5.html', {'name': 'fox', 'tags': list(None)})


def say_hello20(request):
    # -- deleting objects --

    # single
    collection = Collection(pk=11)
    collection.delete()

    # multiple objects
    Collection.objects.filter(id__gt=5).delete()

    return render(request, 'hello5.html', {'name': 'fox', 'tags': list(None)})


def say_hello21(request):
    # transactions: group multiple queries that depend on each other, if one query operation fails rollback everything

    with transaction.atomic():

        order = Order()
        order.customer_id = 1
        order.save()

        item = OrderItem()
        item.order = order
        item.product_id = 1
        item.quantity = 1
        item.unit_price = 10
        item.save()

    return render(request, 'hello5.html', {'name': 'fox', 'tags': list(None)})


def say_hello22(request):
    # execute raw sql queries, and return raw queryset (different from regular queryset, no filter, etc.)
    # only use this with complex queries, for optimization, bypass model layer
    queryset = Product.objects.raw('SELECT id, title FROM store_product')

    # always close cursor even with exception
    with connection.cursor() as cursor_identifier:
        # execute raw sql
        cursor_identifier.execute()
        # execute stored procedures
        cursor_identifier.callproc('get_customers', [1, 2])

    return render(request, 'hello5.html', {'name': 'fox', 'result': list(queryset)})


def say_hello23(request):

    return render(request, 'hello5.html', {'name': 'fox', 'result': list(None)})


def say_hello24(request):
    # email sending test
    try:
        # send_mail(
        #     subject='subject',
        #     message='message',
        #     from_email='info@test.com',
        #     recipient_list=['bob@test.com'],
        # )

        # mail_admins(
        #     subject='sub',
        #     message='msg',
        #     html_message='<b>msg</b>'
        # )

        # message = EmailMessage(
        #     subject='subj',
        #     body='messsage',
        #     from_email='from@test.com',
        #     to=['bob@test.com'],
        # )
        # message.attach_file(
        #     path='playground/static/images/test.txt'
        # )
        # message.send()

        message = BaseEmailMessage(
            template_name='emails/hello.html',
            context={'name': 'testfornow'},

        )
        message.send(to=['bob@test.com'], from_email='mytest@test.com')

    # exception to prevent email header exploit
    except BadHeaderError:
        pass
    return render(request, 'hello5.html', {})


def say_hello25(request):
    notify_customers.delay('hello from say_hello')
    return render(request, 'hello5.html', {})


# low level caching
def say_hello26(request):
    key = 'httpbin_result'

    if cache.get(key) is None:
        # simulate slow 3rd party service
        # data does not exist on cache
        response = requests.get('https://httpbin.org/delay/5')
        data = response.json()
        cache.set(key, data)

    return render(request, 'hello5.html', {'name': cache.get(key)})


# using decorator to cache views
# let django take care of low level api
@cache_page(5*60)
def say_hello(request):
    response = requests.get('https://httpbin.org/delay/5')
    data = response.json()
    return render(request, 'hello5.html', {'name': data})


# __name__ translates to 'playground.views'
logger = logging.getLogger(__name__)


class HelloView(APIView):
    # decorate the decorator
    # @method_decorator(cache_page(5*60))
    def get(self, request):
        try:
            logger.info('Calling httpbin')
            response = requests.get('https://httpbin.org/delay/2')
            logger.info('Received the response')
            data = response.json()
        except requests.ConnectionError:
            logger.critical('httpbin is offline')

        return render(request, 'hello5.html', {'name': data})
