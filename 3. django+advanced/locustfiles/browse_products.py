from locust import HttpUser, task, between
from random import randint


class WebsiteUser(HttpUser):
    # randomly wait between 1-5 second on each task
    wait_time = between(1, 5)

    @task(2)
    def view_products(self):
        print('view products - locust')
        collection_id = randint(2, 6)
        self.client.get(
            f'/store/products/?collection_id={collection_id}',
            name='/store/products')

    # add weight, meaning this has more probability that user access this endpoint
    # higher value indicates higher execution
    @task(4)
    def view_product(self):
        print('view product details - locust')
        product_id = randint(1, 1000)
        self.client.get(
            f'/store/products/{product_id}',
            name='/store/products/:id')

    @task(1)
    def add_to_cart(self):
        print('add to cart - locust')
        product_id = randint(1, 10)
        self.client.post(
            f'/store/carts/{self.cart_id}/items/',
            name='/store/carts/items',
            json={'product_id': product_id, 'quantity': 1}
        )

    @task
    def HelloView(self):
        self.client.get('/playground/hello2/')

    # lifecycle hook, not a task
    def on_start(self):
        response = self.client.post('/store/carts/', name='/store/carts')
        print(response.text)
        result = response.json()
        self.cart_id = result['id']
