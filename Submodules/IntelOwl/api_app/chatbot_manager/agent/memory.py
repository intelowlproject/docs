# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from api_app.chatbot_manager.placeholder_guard import strip_notice


class DjangoChatMessageHistory(BaseChatMessageHistory):
    """LangChain chat history backed by the Django ChatMessage model.

    Implements the BaseChatMessageHistory contract so a ChatSession's messages can be
    used as an agent's conversation memory: `messages` reads, `add_message` writes
    (via the inherited add_user_message/add_ai_message helpers), `clear` resets.
    """

    def __init__(self, session):
        """Bind this history to a single ChatSession (all reads/writes scope to it)."""
        self.session = session

    @property
    def messages(self) -> list[BaseMessage]:
        """Return the session's messages, oldest first, as LangChain message objects."""
        from api_app.chatbot_manager.models import ChatMessage

        result = []
        for msg in ChatMessage.objects.filter(session=self.session).order_by("timestamp"):
            if msg.role == ChatMessage.Role.USER:
                result.append(HumanMessage(content=msg.content))
            else:
                # The placeholder notice is an annotation added for the user after generation, not
                # something the model wrote. Replaying it would put it in the model's context, where
                # a small model may start imitating the format.
                result.append(AIMessage(content=strip_notice(msg.content)))
        return result

    def add_message(self, message: BaseMessage) -> None:
        """Persist one message, mapping its LangChain type to the ChatMessage role."""
        from api_app.chatbot_manager.models import ChatMessage

        role = ChatMessage.Role.USER if isinstance(message, HumanMessage) else ChatMessage.Role.ASSISTANT
        ChatMessage.objects.create(session=self.session, role=role, content=message.content)

    def clear(self) -> None:
        """Delete every message in the session (resets the conversation)."""
        from api_app.chatbot_manager.models import ChatMessage

        ChatMessage.objects.filter(session=self.session).delete()
