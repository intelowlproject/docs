import React from "react";
import axios from "axios";
import "@testing-library/jest-dom";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";

import { ChatSessionList } from "../../../src/components/chat/ChatSessionList";
import { useChatStore } from "../../../src/stores/useChatStore";
import { areYouSureConfirmDialog } from "../../../src/components/common/areYouSureConfirmDialog";

jest.mock("axios");
jest.mock("../../../src/components/common/areYouSureConfirmDialog", () => ({
  areYouSureConfirmDialog: jest.fn(),
}));

const baseState = {
  sessions: [],
  sessionsLoading: false,
  sessionsError: null,
  sessionId: null,
  isStreaming: false,
  navEpoch: 0,
};

// Resolve fetchSessions on mount with the given page payload.
function mockSessionsPage(results) {
  axios.get.mockResolvedValueOnce({ data: { total_pages: 1, results } });
}

describe("ChatSessionList", () => {
  beforeEach(() => {
    useChatStore.setState(baseState);
    jest.clearAllMocks();
  });

  test("renders a row per fetched session with its backend-provided title", async () => {
    mockSessionsPage([
      { id: 1, created_at: "2026-06-11T14:02:00Z", title: "my first question" },
    ]);
    render(<ChatSessionList onSessionChosen={jest.fn()} />);
    expect(await screen.findByText("my first question")).toBeInTheDocument();
    expect(screen.getByText("2026-06-11 14:02")).toBeInTheDocument();
  });

  test("shows the empty state when there are no sessions", async () => {
    mockSessionsPage([]);
    render(<ChatSessionList onSessionChosen={jest.fn()} />);
    expect(
      await screen.findByText(/No conversations yet/i),
    ).toBeInTheDocument();
  });

  test("shows an error alert when the fetch fails", async () => {
    axios.get.mockRejectedValueOnce(new Error("boom"));
    render(<ChatSessionList onSessionChosen={jest.fn()} />);
    expect(await screen.findByText(/conversations/i)).toBeInTheDocument();
  });

  test("selecting a row switches session and returns to the conversation", async () => {
    const switchSession = jest.fn();
    const onSessionChosen = jest.fn();
    useChatStore.setState({ switchSession });
    mockSessionsPage([
      { id: 7, created_at: "2026-06-11T14:02:00Z", title: "pick me" },
    ]);
    render(<ChatSessionList onSessionChosen={onSessionChosen} />);
    fireEvent.click(await screen.findByText("pick me"));
    expect(switchSession).toHaveBeenCalledWith(7);
    expect(onSessionChosen).toHaveBeenCalled();
  });

  test("New chat starts a fresh conversation and returns to the conversation", async () => {
    const newChat = jest.fn();
    const onSessionChosen = jest.fn();
    useChatStore.setState({ newChat });
    mockSessionsPage([]);
    render(<ChatSessionList onSessionChosen={onSessionChosen} />);
    fireEvent.click(screen.getByRole("button", { name: /New chat/i }));
    expect(newChat).toHaveBeenCalled();
    expect(onSessionChosen).toHaveBeenCalled();
  });

  test("delete asks for confirmation and deletes when confirmed", async () => {
    const deleteSession = jest.fn();
    useChatStore.setState({ deleteSession });
    areYouSureConfirmDialog.mockResolvedValueOnce(true);
    mockSessionsPage([{ id: 3, created_at: "2026-06-11T14:02:00Z" }]);
    render(<ChatSessionList onSessionChosen={jest.fn()} />);
    fireEvent.click(
      await screen.findByRole("button", { name: /Delete conversation/i }),
    );
    await waitFor(() => expect(deleteSession).toHaveBeenCalledWith(3));
  });

  test("delete does nothing when the confirmation is dismissed", async () => {
    const deleteSession = jest.fn();
    useChatStore.setState({ deleteSession });
    areYouSureConfirmDialog.mockResolvedValueOnce(false);
    mockSessionsPage([{ id: 3, created_at: "2026-06-11T14:02:00Z" }]);
    render(<ChatSessionList onSessionChosen={jest.fn()} />);
    fireEvent.click(
      await screen.findByRole("button", { name: /Delete conversation/i }),
    );
    await waitFor(() => expect(areYouSureConfirmDialog).toHaveBeenCalled());
    expect(deleteSession).not.toHaveBeenCalled();
  });

  test("switching sessions while streaming proceeds (navigation is not locked)", async () => {
    const switchSession = jest.fn();
    const onSessionChosen = jest.fn();
    useChatStore.setState({ isStreaming: true, switchSession });
    mockSessionsPage([
      { id: 1, created_at: "2026-06-11T14:02:00Z", title: "a row" },
    ]);
    render(<ChatSessionList onSessionChosen={onSessionChosen} />);
    // New chat is enabled even while streaming
    expect(
      screen.getByRole("button", { name: /New chat/i }),
    ).not.toBeDisabled();
    fireEvent.click(await screen.findByText("a row"));
    expect(switchSession).toHaveBeenCalledWith(1);
    expect(onSessionChosen).toHaveBeenCalled();
  });
});
