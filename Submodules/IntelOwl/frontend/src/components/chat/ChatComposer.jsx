import React from "react";
import PropTypes from "prop-types";
import { Button, Input } from "reactstrap";
import { IoSend } from "react-icons/io5";

import { useChatStore, ConnectionState } from "../../stores/useChatStore";

// Mirror MessageRequestSerializer(message=CharField(max_length=4096)) so the UI caps input before
// the server rejects it with INVALID_MESSAGE.
const MAX_MESSAGE_LEN = 4096;

/**
 * Message input. Enter sends, Shift+Enter inserts a newline. Disabled while a turn is streaming or
 * the socket is not connected, so the user can't fire a second turn before the first finishes.
 */
export function ChatComposer({ onSend }) {
  const [text, setText] = React.useState("");
  const isStreaming = useChatStore((state) => state.isStreaming);
  const connectionState = useChatStore((state) => state.connectionState);
  const disabled = isStreaming || connectionState !== ConnectionState.CONNECTED;

  const submit = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  };

  return (
    <div className="d-flex align-items-end p-2 border-top">
      <Input
        id="chat-composer-input"
        type="textarea"
        rows={1}
        value={text}
        maxLength={MAX_MESSAGE_LEN}
        placeholder="Ask about your threat intel data…"
        onChange={(event) => setText(event.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
      />
      <Button
        color="primary"
        className="ms-2"
        onClick={submit}
        disabled={disabled || !text.trim()}
        aria-label="Send message"
      >
        <IoSend />
      </Button>
    </div>
  );
}

ChatComposer.propTypes = {
  onSend: PropTypes.func.isRequired,
};
