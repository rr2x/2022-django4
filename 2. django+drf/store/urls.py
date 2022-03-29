from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# router combines with ViewSet
router = DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('collections', views.CollectionViewSet)

# DefaultRouter shows other api links on it's main url (../store/)
# it also allows you to get the .json of a list
# example: ../store/products.json

urlpatterns = [
    path('', include(router.urls)),
]


# urlpatterns = [
# path('products/', views.product_list),
# # converter; <int:...>
# path('products/<int:id>/', views.product_detail),
# path('collections/', views.collection_list),
# path('collections/<int:pk>/', views.collection_detail),

# path('products/', views.ProductList.as_view()),
# path('products/<int:pk>/', views.ProductDetail.as_view()),
# path('collections/', views.CollectionList.as_view()),
# path('collections/<int:pk>/', views.CollectionDetail.as_view()),
# ]
