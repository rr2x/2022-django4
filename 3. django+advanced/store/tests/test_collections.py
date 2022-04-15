# best practices:
#   be descriptive on test names to tell what behavior we are testing
#   AAA; Arrange -> Act -> Assert

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
import pytest


# all methods will inherit this decorator
@pytest.mark.django_db
class TestCreateCollection:
    # @pytest.mark.skip    # use this decorator if you want to skip this test for now
    def test_if_user_is_anonymous_returns_401(self):
        # Arrange

        # Act
        client = APIClient()
        response = client.post('/store/collections/', {'title': 'a'})

        # Assert (check if we got the behavior we expect)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self):
        client = APIClient()
        client.force_authenticate(user={})
        response = client.post('/store/collections/', {'title': 'a'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self):
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))
        response = client.post('/store/collections/', {'title': ''})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_if_data_is_valid_returns_201(self):
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))
        response = client.post('/store/collections/', {'title': 'a'})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0
