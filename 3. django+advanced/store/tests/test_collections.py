# best practices:
#   be descriptive on test names to tell what behavior we are testing
#   AAA; Arrange -> Act -> Assert

from store.models import Collection, Product
from rest_framework import status
import pytest
from model_bakery import baker  # to easily create objects

# note = pytest always creates "test_<database_name>" database
# and after running all tests, it drop that database


# define local fixture that is only used here
# api_client fixture is extracted from conftest.py
@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post('/store/collections/', collection)
    return do_create_collection  # return a function, closure pattern


# all methods will inherit this decorator
@pytest.mark.django_db
class TestCreateCollection:

    # @pytest.mark.skip    # use this decorator if you want to skip this test for now
    # create_collection is a local fixture
    def test_if_user_is_anonymous_returns_401(self, create_collection):
        # arrange
        # act
        response = create_collection({'title': 'a'})
        # assert (check if we got the behavior we expect)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # authenticate global fixture is extracted from conftest.py
    def test_if_user_is_not_admin_returns_403(self, authenticate, create_collection):
        # arrange
        authenticate()
        # act
        response = create_collection({'title': 'a'})
        # assert (check if we got the behavior we expect)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, authenticate, create_collection):
        authenticate(is_staff=True)
        response = create_collection({'title': ''})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_if_data_is_valid_returns_201(self, authenticate, create_collection):
        authenticate(is_staff=True)
        response = create_collection({'title': 'a'})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0


@pytest.mark.django_db
class TestRetrieveCollection:
    def test_if_collection_exists_returns_200(self, api_client):
        collection = baker.make(Collection)

        response = api_client.get(f'/store/collections/{collection.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': collection.id,
            'title': collection.title,
            'products_count': 0
        }
