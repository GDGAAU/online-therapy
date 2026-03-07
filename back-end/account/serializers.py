from rest_framework import serializers
from .models import Profile, User


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', required=False)
    profile_image = serializers.ImageField(required=False, allow_null=True)

    user_id = serializers.UUIDField(source='user.id', read_only=True)
    verified = serializers.BooleanField(
        source='user.is_verified', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'username', 'user_id', 'verified',
            'first_name', 'last_name', 'bio',
            'occupation', 'location', 'contact_info',
            'profile_image', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'verified', 'user_id']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        new_username = user_data.get('username')

        if new_username:
            new_username = new_username.strip()

            if new_username == "":
                raise serializers.ValidationError(
                    {"username": "Username cannot be empty"}
                )

            if User.objects.filter(username=new_username)\
                           .exclude(id=instance.user.id).exists():
                raise serializers.ValidationError(
                    {"username": "Username is already taken"}
                )

            instance.user.username = new_username
            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance