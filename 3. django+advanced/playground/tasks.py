from time import sleep
from celery import shared_task


# this is best practice, decouple storefront from this app
@shared_task
def notify_customers(message):
    print('sending 10k emails')
    print(message)
    sleep(10)
    print('emails were successfully sent!')
    print('--no more emails--')
