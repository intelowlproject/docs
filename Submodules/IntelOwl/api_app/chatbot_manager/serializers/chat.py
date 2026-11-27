# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

from rest_framework import serializers

from ..models import ChatMessage, ChatSession


class ChatSessionSerializer(serializers.ModelSerializer):
    title = serializers.CharField(read_only=True, default=None)

    class Meta:
        model = ChatSession
        fields = ["id", "created_at", "updated_at", "title"]
        read_only_fields = ["id", "created_at", "updated_at", "title"]


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "role", "content", "timestamp"]
        read_only_fields = ["id", "timestamp"]


class MessageRequestSerializer(serializers.Serializer):
    session_id = serializers.IntegerField(required=False, allow_null=True)
    message = serializers.CharField(max_length=4096)


class MessageResponseSerializer(serializers.Serializer):
    # Serializes the persisted assistant ChatMessage directly (no hand-built dict).
    session_id = serializers.IntegerField()
    response = serializers.CharField(source="content")
    message_id = serializers.IntegerField(source="id")
