# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

from django.test import TestCase
from langchain_core.messages import AIMessage, HumanMessage

from api_app.chatbot_manager.agent.memory import DjangoChatMessageHistory
from api_app.chatbot_manager.models import ChatMessage, ChatSession
from api_app.chatbot_manager.placeholder_guard import PLACEHOLDER_NOTICE, guard_answer
from certego_saas.apps.user.models import User


class DjangoChatMessageHistoryTestCase(TestCase):
    """History is what the model re-reads each turn, so the guard's annotation must not ride along."""

    def setUp(self):
        self.user, _ = User.objects.get_or_create(username="chatbot_memory_user")
        self.session = ChatSession.objects.create(user=self.user)

    def _add(self, role, content):
        ChatMessage.objects.create(session=self.session, role=role, content=content)

    def test_the_placeholder_notice_is_not_replayed_into_the_prompt(self):
        answer = "Use [Playbook X]."
        self._add(ChatMessage.Role.USER, "which playbook?")
        self._add(ChatMessage.Role.ASSISTANT, guard_answer(answer, session_id=self.session.id))

        messages = DjangoChatMessageHistory(session=self.session).messages

        self.assertEqual(
            [(type(message), message.content) for message in messages],
            [(HumanMessage, "which playbook?"), (AIMessage, answer)],
        )

    def test_a_user_message_is_replayed_verbatim(self):
        # Only assistant rows are annotated by the guard, so a user who happens to paste the same
        # text must get it back unchanged.
        self._add(ChatMessage.Role.USER, f"look at this: {PLACEHOLDER_NOTICE}")

        messages = DjangoChatMessageHistory(session=self.session).messages

        self.assertEqual(messages[0].content, f"look at this: {PLACEHOLDER_NOTICE}")

    def test_an_unannotated_assistant_answer_is_replayed_verbatim(self):
        self._add(ChatMessage.Role.ASSISTANT, "Job #42 is malicious.")

        messages = DjangoChatMessageHistory(session=self.session).messages

        self.assertEqual(messages[0].content, "Job #42 is malicious.")
