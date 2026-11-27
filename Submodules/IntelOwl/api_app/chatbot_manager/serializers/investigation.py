# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

from rest_framework import serializers

from api_app.investigations_manager.models import Investigation

from .base import ToolResultSerializer


class InvestigationToolSerializer(serializers.ModelSerializer):
    """Compact, LLM-facing Investigation view for list results (no owner/PII fields).

    Deliberately exposes only DB columns. `Investigation.tlp`, `.tags` and `.total_jobs`
    are @properties that each query the `jobs` relation, so including them here would fire
    extra queries for every row (N+1 across a list). Those aggregate fields are surfaced
    instead by `summarize_investigation` / `get_investigation_tree`, which operate on a
    single investigation where the cost is bounded.
    """

    class Meta:
        model = Investigation
        fields = ["id", "name", "status", "start_time", "end_time"]


class InvestigationsResultSerializer(ToolResultSerializer):
    investigations = InvestigationToolSerializer(many=True)


class InvestigationTreeResultSerializer(ToolResultSerializer):
    # The tree is assembled in Python (in the tool) to avoid the treebeard per-node N+1,
    # so the payload is already a plain nested dict; the envelope only JSON-serializes it.
    investigation = serializers.DictField(read_only=True, allow_null=True)


class SummarizeInvestigationResultSerializer(ToolResultSerializer):
    summary = serializers.CharField(allow_null=True)
