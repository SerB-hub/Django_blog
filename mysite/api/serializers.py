from rest_framework import serializers
from django.contrib.auth.models import User
from blog.models import Post, Comment, Category


class CategorySerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    posts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'author', 'posts']


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    comments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'author', 'comments', 'categories', 'comments']


class UserSerializer(serializers.ModelSerializer):
    blog_posts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    comments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    categories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # Вместо списка id можно возвращать список URL с помощью HyperlinkedModelSerializer

    class Meta:
        model = User
        fields = ['id', 'username', 'blog_posts', 'comments', 'categories']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'body', 'author', 'post']
