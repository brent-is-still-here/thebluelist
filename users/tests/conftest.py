import pytest
from django.contrib.auth import get_user_model
import factory
from faker import Faker

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
    
    username = factory.LazyFunction(lambda: fake.user_name())
    email = factory.LazyFunction(lambda: fake.email())
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')

@pytest.fixture
def user_factory():
    return UserFactory

@pytest.fixture
def authenticated_client(client, user_factory):
    user = user_factory()
    client.force_login(user)
    return client