import React from "react";
import PropTypes from "prop-types";

import { chatMarkdownToHtml } from "./chatMarkdown";
import { MessageRole } from "../../stores/useChatStore";

/**
 * A single chat bubble. User messages render as plain (newline-preserving) text and align right;
 * assistant messages render markdown (GFM) and align left.
 */
export function ChatMessage({ role, content }) {
  const isUser = role === MessageRole.USER;
  return (
    <div
      className={`d-flex mb-2 ${
        isUser ? "justify-content-end" : "justify-content-start"
      }`}
    >
      <div
        className={`px-3 py-2 rounded ${
          isUser
            ? "bg-primary text-white"
            : "bg-dark text-white border border-secondary"
        }`}
        style={{ maxWidth: "85%", wordBreak: "break-word" }}
      >
        {isUser ? (
          <span style={{ whiteSpace: "pre-wrap" }}>{content}</span>
        ) : (
          chatMarkdownToHtml(content)
        )}
      </div>
    </div>
  );
}

ChatMessage.propTypes = {
  role: PropTypes.string.isRequired,
  content: PropTypes.string.isRequired,
};
