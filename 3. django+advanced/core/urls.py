from django.views.generic import TemplateView
from django.urls import path
from . import views

urlpatterns = [
    # namespaced template
    path('', TemplateView.as_view(template_name='core/index.html')),
]
