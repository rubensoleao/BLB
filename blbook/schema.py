# cookbook/schema.py
import graphene
import graphql_jwt
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.signals import request_finished
from graphene_django import DjangoObjectType

from blbook.posts.models import Post


class UserType(DjangoObjectType):
    class Meta:
        model=User
        fields=("id", "username", "email", "password")

class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = ("id", "text", "posted_by")
        

class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)

    def resolve_all_users(root, info):
        # We can easily optimize query count in the resolve method
        return User.objects.all()

class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)
    success = graphene.Boolean()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, username, password, email):
        user = get_user_model()(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()

        return CreateUser(user=user, success=True)

class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    register = CreateUser.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)