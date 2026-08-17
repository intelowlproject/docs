# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

from rest_framework import serializers

from api_app.analyzers_manager.models import AnalyzerConfig

from .base import ToolResultSerializer


class AnalyzerConfigToolSerializer(serializers.ModelSerializer):
    """Compact, LLM-facing AnalyzerConfig view for list_analyzers (no owner/PII fields).

    `runnable` is read from a per-user queryset annotation (`annotate_runnable`): True means
    ready to run for the requesting user, False means org-disabled or not fully configured. It
    is a readiness flag, not a visibility filter -- the analyzer is listed either way.
    """

    # `observable_supported` is a ChoiceArrayField; DRF's ModelSerializer does not auto-map it,
    # so declare it explicitly (same approach as the heavy PlaybookConfigSerializer's `type`).
    observable_supported = serializers.ListField(child=serializers.CharField(), read_only=True)
    runnable = serializers.BooleanField(read_only=True)

    class Meta:
        model = AnalyzerConfig
        fields = ["name", "description", "type", "observable_supported", "maximum_tlp", "runnable"]


class ListAnalyzersResultSerializer(ToolResultSerializer):
    analyzers = AnalyzerConfigToolSerializer(many=True)
