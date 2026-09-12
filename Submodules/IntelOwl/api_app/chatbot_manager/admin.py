# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

from django.contrib import admin

from api_app.chatbot_manager.models import ChatMessage, ChatSession


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ["pk", "user", "created_at", "updated_at"]
    list_filter = ["user", "created_at"]
    ordering = ["-created_at"]
    search_fields = ["user__username"]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ["pk", "session", "role", "timestamp"]
    list_filter = ["role", "timestamp"]
    ordering = ["timestamp"]
    search_fields = ["content"]
