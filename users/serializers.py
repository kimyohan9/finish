from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile


User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password',]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture', 'location']  # 프로필에 포함할 필드

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()  # 유저와 연결된 프로필 정보도 포함

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'profile']  # 유저 모델에 포함될 필드

    def update(self, instance, validated_data):
        # 유저 프로필 정보 업데이트
        profile_data = validated_data.pop('profile', None)

        # 유저 정보 업데이트
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])  # 비밀번호는 set_password로 변경해야 함
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 프로필 정보 업데이트
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance
