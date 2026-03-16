from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "client_id",
            "secret_key"
        ]

        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate_email(self, value):

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User already exists")

        return value


    def validate_client_id(self, value):

        if User.objects.filter(client_id=value).exists():
            raise serializers.ValidationError("Client ID already registered")

        return value


    def create(self, validated_data):

        validated_data["password"] = make_password(validated_data["password"])

        return User.objects.create(**validated_data)


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField()