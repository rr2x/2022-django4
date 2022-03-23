from django.db import models

# all related classes are inside store to avoid external dependencies
# if exporting the app into another project


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()


class Collection(models.Model):
    title = models.CharField(max_length=255)
    # related_name='+' to prevent django creating a reverse relationship
    # which conflicts with Product class (it will create product_set__ reverse relation)
    # promotion already owns 'product_set__' reverse relation
    # featured_product links to an existing product_id
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True, related_name='+')


class Product(models.Model):
    title = models.CharField(max_length=255)
    # slug for SEO url technique
    slug = models.SlugField()
    description = models.TextField()
    # max value: 9999.99
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)

    # on_delete=models.PROTECT = if you delete a row from Collection table, don't delete on this
    # (one to many) 1 collection can have multiple products
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)

    # multiple promotions, will also create reverse relationship to Promotion table
    # related_name='...' name of the reverse relationship, override instead of default "promotion_set__..."
    promotions = models.ManyToManyField(Promotion, related_name='products')


class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold'),
    ]
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE)


class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed'),
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    # on_delete=models.PROTECT = if you delete a row from Customer table, don't delete on this
    # because it represents our sales
    # (one to many) 1 customer can have multiple orders
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    # to access product from order item with "reverse relation name":
    #   orderitem_set__product


class OrderItem(models.Model):
    # orderitem_set as name of "reverse relationship" from Order (set by default of Django)
    # can edit name via related_name='...' attribute
    # (one to many) 1 order can have multiple orderitems
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    # (one to many) 1 product can be linked to multiple orderitems
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    # prevent negative values from being stored
    quantity = models.PositiveSmallIntegerField()
    # because prices can change overtime, so store it at the time it was ordered
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zip = models.CharField(max_length=50)
    # on_delete=models.CASCADE = if parent deleted, delete this too
    # on_delete=models.SET_NULL = if parent deleted, linking attribute becomes null and this will not be deleted
    # on_delete=models.SET_DEFAULT = set with default value if parent deleted
    # primary_key=True = don't allow duplicate values, will not make primary id for this table
    # customer = models.OneToOneField(Customer, on_delete=models.CASCADE, primary_key=True)

    # (one to many) 1 customer can have multiple addresses
    # if we delete a row from Customer table, then delete this too
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    # (one to many) 1 cart can have multiple cartitems
    # if we delete a row from Cart table, then delete this too
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    # (one to many) 1 product can be linked to multiple cartitems
    # if we delete a row from Product table, then delete this too
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
