import React from "react";
import "@testing-library/jest-dom";
import { render, screen, fireEvent } from "@testing-library/react";

import { ChatComposer } from "../../../src/components/chat/ChatComposer";
import {
  useChatStore,
  ConnectionState,
} from "../../../src/stores/useChatStore";

const connectedIdle = {
  isStreaming: false,
  connectionState: ConnectionState.CONNECTED,
};

describe("ChatComposer", () => {
  beforeEach(() => {
    useChatStore.setState(connectedIdle);
  });

  test("Enter sends the trimmed text and clears the input", () => {
    const onSend = jest.fn();
    render(<ChatComposer onSend={onSend} />);
    const input = screen.getByPlaceholderText(/Ask about/i);
    fireEvent.change(input, { target: { value: "  list my jobs  " } });
    fireEvent.keyDown(input, { key: "Enter" });
    expect(onSend).toHaveBeenCalledWith("list my jobs");
    expect(input).toHaveValue("");
  });

  test("Shift+Enter does not send (newline)", () => {
    const onSend = jest.fn();
    render(<ChatComposer onSend={onSend} />);
    const input = screen.getByPlaceholderText(/Ask about/i);
    fireEvent.change(input, { target: { value: "first line" } });
    fireEvent.keyDown(input, { key: "Enter", shiftKey: true });
    expect(onSend).not.toHaveBeenCalled();
  });

  test("empty/whitespace input does not send", () => {
    const onSend = jest.fn();
    render(<ChatComposer onSend={onSend} />);
    const input = screen.getByPlaceholderText(/Ask about/i);
    fireEvent.change(input, { target: { value: "   " } });
    fireEvent.keyDown(input, { key: "Enter" });
    expect(onSend).not.toHaveBeenCalled();
  });

  test("disabled while a turn is streaming", () => {
    useChatStore.setState({
      isStreaming: true,
      connectionState: ConnectionState.CONNECTED,
    });
    render(<ChatComposer onSend={jest.fn()} />);
    expect(screen.getByPlaceholderText(/Ask about/i)).toBeDisabled();
  });

  test("disabled while the socket is not connected", () => {
    useChatStore.setState({
      isStreaming: false,
      connectionState: ConnectionState.RECONNECTING,
    });
    render(<ChatComposer onSend={jest.fn()} />);
    expect(screen.getByPlaceholderText(/Ask about/i)).toBeDisabled();
  });
});
