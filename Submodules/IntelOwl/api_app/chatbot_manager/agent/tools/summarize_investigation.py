# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

from collections import Counter

from langchain_core.tools import tool

from api_app.chatbot_manager.serializers.investigation import SummarizeInvestigationResultSerializer
from api_app.investigations_manager.models import Investigation


def make_summarize_investigation_tool(user):
    # Built per-request and closed over `user`. Scoped with `visible_for_user` (owned +
    # organization-shared investigations). The payload is human-readable prose wrapped in
    # the same envelope as the other tools (LangChain needs a string Observation).
    @tool("summarize_investigation")
    def summarize_investigation(investigation_id: int) -> str:
        """Return a concise human-readable summary of an IntelOwl investigation.

        Includes the status, total jobs, a per-status breakdown of the jobs, TLP, tags and
        the start/end times.

        Args:
            investigation_id: The numeric ID of the investigation to summarize.

        Returns:
            JSON string with shape {"errors": [...], "summary": "..." | null}.
        """
        try:
            investigation = Investigation.objects.visible_for_user(user).get(pk=investigation_id)
        except Investigation.DoesNotExist:
            return SummarizeInvestigationResultSerializer(
                {
                    "errors": [f"Investigation with ID {investigation_id} not found or not accessible."],
                    "summary": None,
                }
            ).to_json()

        # Count jobs by status across the whole tree. `investigation.jobs` are the roots;
        # the rest live in the treebeard tree, so we walk each subtree once (one query per
        # root, status column only) rather than per node.
        status_counts = Counter()
        for root in investigation.jobs.all():
            status_counts[root.status] += 1
            for child_status in root.get_descendants().values_list("status", flat=True):
                status_counts[child_status] += 1

        # The total equals Investigation.total_jobs but is derived from the counts we
        # already gathered, so we don't re-query the tree.
        total_jobs = sum(status_counts.values())
        tags = [label for label in investigation.tags if label]

        lines = [
            f"Investigation #{investigation.pk}: {investigation.name}",
            f"  Status     : {investigation.status}",
            f"  Total jobs : {total_jobs}",
            f"  TLP        : {investigation.tlp}",
        ]
        if status_counts:
            breakdown = ", ".join(f"{status}: {count}" for status, count in sorted(status_counts.items()))
            lines.append(f"  Job status : {breakdown}")
        if tags:
            lines.append(f"  Tags       : {', '.join(tags)}")
        lines.append(f"  Started    : {investigation.start_time}")
        lines.append(f"  Ended      : {investigation.end_time or 'N/A'}")

        return SummarizeInvestigationResultSerializer({"errors": [], "summary": "\n".join(lines)}).to_json()

    return summarize_investigation
