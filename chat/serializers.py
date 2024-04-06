from rest_framework import serializers
from django.contrib.contenttypes.fields import ContentType

from chat.models import Message, Text, Audio, Image, File

from users.api.serializers import UserSerializer


class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text
        fields = ("id", "content")


class AudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audio
        fields = ("id", "content")


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("id", "content")


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ("id", "content")


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    reciever = UserSerializer(read_only=True)
    content = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            "id",
            "sender",
            "reciever",
            "content",
            "is_read",
            "content_type",
            "created_at",
            "updated_at",
        )

    def get_content(self, obj):
        if obj.content_type == ContentType.objects.get_for_model(Text):
            return TextSerializer(obj.text_related.get()).data
        elif obj.content_type == ContentType.objects.get_for_model(Audio):
            return AudioSerializer(obj.audio_related.get()).data
        elif obj.content_type == ContentType.objects.get_for_model(Image):
            return ImageSerializer(obj.image_related.get()).data
        elif obj.content_type == ContentType.objects.get_for_model(File):
            return FileSerializer(obj.file_related.get()).data
        else:
            return None


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            "sender",
            "reciever",
            "content",
            "is_read",
        )
