import React from "react";
import { Spinner } from "reactstrap";

import { ChatMessage } from "./ChatMessage";
import { useChatStore, MessageRole } from "../../stores/useChatStore";

/**
 * Scrollable conversation view: committed messages, plus the in-progress assistant turn (a
 * "Running <tool>…/Thinking…" indicator before any text arrives, then the live streaming bubble).
 * Autoscrolls to the bottom as new content lands.
 */
export function ChatMessageList() {
  const messages = useChatStore((state) => state.messages);
  const streamingText = useChatStore((state) => state.streamingText);
  const currentTool = useChatStore((state) => state.currentTool);
  const isStreaming = useChatStore((state) => state.isStreaming);
  const historyLoading = useChatStore((state) => state.historyLoading);
  const bottomRef = React.useRef(null);

  React.useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingText, currentTool]);

  return (
    <div className="flex-grow-1 overflow-auto p-3">
      {historyLoading && (
        <div className="text-center p-3">
          <Spinner size="sm" />
        </div>
      )}
      {messages.map((message, index) => (
        <ChatMessage
          // committed assistant messages carry a server id; user messages fall back to position
          key={message.id ?? `${message.role}-${index}`}
          role={message.role}
          content={message.content}
        />
      ))}
      {isStreaming && !streamingText && (
        <div className="text-muted small mb-2 d-flex align-items-center">
          <Spinner size="sm" className="me-2" />
          {currentTool ? `Running ${currentTool}…` : "Thinking…"}
        </div>
      )}
      {isStreaming && streamingText && (
        <ChatMessage role={MessageRole.ASSISTANT} content={streamingText} />
      )}
      <div ref={bottomRef} />
    </div>
  );
}
