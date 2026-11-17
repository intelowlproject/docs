# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

from django.conf import settings
from django.db import models
from django.utils.timezone import now


class ChatSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions",
    )
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"ChatSession #{self.pk} ({self.user})"


class ChatMessage(models.Model):
    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=16, choices=Role.choices)
    content = models.TextField()
    timestamp = models.DateTimeField(default=now, editable=False, db_index=True)

    class Meta:
        ordering = ["timestamp"]
        indexes = [models.Index(fields=["session", "timestamp"])]

    def __str__(self) -> str:
        preview = self.content[:50] + ("…" if len(self.content) > 50 else "")
        return f"[{self.role}] {preview}"
