from djoser.serializers import \
    UserCreateSerializer as BaseUserCreateSerializer, \
    UserSerializer as BaseUserSerializer


# https://djoser.readthedocs.io/en/latest/settings.html?highlight=serializer#serializers

class UserCreateSerializer(BaseUserCreateSerializer):

    class Meta(BaseUserCreateSerializer.Meta):
        # override fields of djoser
        fields = ['id', 'username', 'password',
                  'email', 'first_name', 'last_name']


class UserSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
