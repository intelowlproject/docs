# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

from rest_framework import serializers

from api_app.playbooks_manager.models import PlaybookConfig

from .base import ToolResultSerializer


class PlaybookConfigToolSerializer(serializers.ModelSerializer):
    """Compact, LLM-facing PlaybookConfig view for recommend_playbook (no owner/PII fields)."""

    # `type` is a ChoiceArrayField of classifications; declare it explicitly (DRF doesn't auto-map
    # it). `analyzers`/`connectors` are M2M relations rendered as their names.
    type = serializers.ListField(child=serializers.CharField(), read_only=True)
    analyzers = serializers.SlugRelatedField(slug_field="name", many=True, read_only=True)
    connectors = serializers.SlugRelatedField(slug_field="name", many=True, read_only=True)

    class Meta:
        model = PlaybookConfig
        fields = ["name", "description", "type", "analyzers", "connectors"]


class RecommendPlaybookResultSerializer(ToolResultSerializer):
    playbooks = PlaybookConfigToolSerializer(many=True)
