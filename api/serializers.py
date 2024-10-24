from rest_framework import serializers
from .models import User, UserProfile


class RegisterSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False, max_length=15)
    profile_picture = serializers.ImageField(required=False)
    address = serializers.CharField(required=False)
    date_of_birth = serializers.DateField(required=False)

    password = serializers.CharField(write_only=True)
    date_joined = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "date_joined",
            "password",
            "phone_number",
            "profile_picture",
            "address",
            "date_of_birth",
        ]

    def create(self, validated_data):
        phone_number = validated_data.pop("phone_number", None)
        profile_picture = validated_data.pop("profile_picture", None)
        address = validated_data.pop("address", None)
        date_of_birth = validated_data.pop("date_of_birth", None)

        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )

        UserProfile.objects.create(
            user=user,
            phone_number=phone_number,
            date_of_birth=date_of_birth,
            profile_picture=profile_picture,
            address=address,
        )

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source="profile.phone_number", required=False)
    profile_picture = serializers.ImageField(
        source="profile.profile_picture", required=False
    )
    address = serializers.CharField(source="profile.address", required=False)
    date_of_birth = serializers.DateField(
        source="profile.date_of_birth", required=False
    )

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "date_joined",
            "phone_number",
            "date_of_birth",
            "profile_picture",
            "address",
        ]
        read_only_fields = ["email", "username", "date_joined"]

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)

        profile = instance.profile

        profile_data = validated_data.get("profile")

        for field in profile_data:
            value = profile_data.get(field)
            if value is not None:
                setattr(profile, field, value)

        profile.save()
        return instance
