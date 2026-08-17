import React from "react";
import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";

import { ChatMessageList } from "../../../src/components/chat/ChatMessageList";
import { useChatStore, MessageRole } from "../../../src/stores/useChatStore";

const emptyTurn = {
  messages: [],
  streamingText: "",
  currentTool: null,
  isStreaming: false,
};

describe("ChatMessageList", () => {
  beforeAll(() => {
    // jsdom does not implement scrollIntoView; the autoscroll effect calls it.
    window.HTMLElement.prototype.scrollIntoView = jest.fn();
  });

  beforeEach(() => {
    useChatStore.setState(emptyTurn);
  });

  test("renders committed user and assistant messages", () => {
    useChatStore.setState({
      messages: [
        { role: MessageRole.USER, content: "hello" },
        { id: 9, role: MessageRole.ASSISTANT, content: "**hi there**" },
      ],
    });
    render(<ChatMessageList />);
    expect(screen.getByText("hello")).toBeInTheDocument();
    expect(screen.getByText("hi there").tagName).toBe("STRONG");
  });

  test("shows the running-tool indicator before any token streams", () => {
    useChatStore.setState({
      isStreaming: true,
      streamingText: "",
      currentTool: "search_jobs",
    });
    render(<ChatMessageList />);
    expect(screen.getByText(/Running search_jobs/i)).toBeInTheDocument();
  });

  test("shows a generic thinking indicator when no tool is running yet", () => {
    useChatStore.setState({ isStreaming: true, streamingText: "" });
    render(<ChatMessageList />);
    expect(screen.getByText(/Thinking/i)).toBeInTheDocument();
  });

  test("renders the in-progress streaming bubble", () => {
    useChatStore.setState({
      isStreaming: true,
      streamingText: "partial answer",
    });
    render(<ChatMessageList />);
    expect(screen.getByText("partial answer")).toBeInTheDocument();
  });

  test("shows a loading spinner while a session's history is loading", () => {
    useChatStore.setState({ historyLoading: true });
    render(<ChatMessageList />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });
});
