import React from "react";
import axios from "axios";
import "@testing-library/jest-dom";
import {
  render,
  screen,
  act,
  fireEvent,
  waitFor,
  within,
} from "@testing-library/react";

import { ChatPanel } from "../../../src/components/chat/ChatPanel";
import {
  useChatStore,
  ConnectionState,
} from "../../../src/stores/useChatStore";

jest.mock("axios");

// Controllable WebSocket: opens on the next tick (CONNECTING -> CONNECTED) and exposes the live
// instance so the test can push server frames (emit) and assert what the client sent.
let liveSocket = null;
class ControllableWebSocket {
  constructor() {
    this.readyState = ControllableWebSocket.OPEN;
    this.sent = [];
    liveSocket = this;
    setTimeout(() => {
      if (this.onopen) this.onopen({});
    }, 0);
  }

  send(data) {
    this.sent.push(JSON.parse(data));
  }

  // eslint-disable-next-line class-methods-use-this
  close() {}

  emit(frame) {
    if (this.onmessage) this.onmessage({ data: JSON.stringify(frame) });
  }
}
ControllableWebSocket.OPEN = 1;

// Reset the store data fields between tests WITHOUT replacing the action reducers (merge, no `true`).
const baseState = {
  isOpen: true,
  sessionId: null,
  messages: [],
  streamingText: "",
  currentTool: null,
  isStreaming: false,
  connectionState: ConnectionState.IDLE,
  error: null,
  sessions: [],
  sessionsLoading: false,
  sessionsError: null,
  historyLoading: false,
  navEpoch: 0,
  assistantUnavailable: false,
  pendingAction: null,
};

const SESSION_ID = 11;
const PENDING_ID = "pending-abc";
const PLAN = {
  observable_name: "example.com",
  classification: "domain",
  tlp: "CLEAR",
  playbook: null,
  analyzers: ["Tranco"],
  connectors: [],
  skipped: [],
};

describe("ChatPanel E2E (full turn -> confirm)", () => {
  beforeAll(() => {
    window.HTMLElement.prototype.scrollIntoView = jest.fn();
  });

  beforeEach(() => {
    liveSocket = null;
    global.WebSocket = ControllableWebSocket;
    useChatStore.setState(baseState);
    axios.get.mockImplementation((url) =>
      url.includes("/health")
        ? Promise.resolve({ data: { available: true, detail: "" } })
        : Promise.resolve({ data: { total_pages: 1, results: [] } }),
    );
    // confirmAnalysis() POSTs to the confirm endpoint
    axios.post.mockResolvedValue({
      data: { errors: [], reused: false, job: { id: 99, status: "pending" } },
    });
  });

  test("streams a tool-call turn to the confirm card and launches the analysis", async () => {
    render(<ChatPanel />);
    expect(await screen.findByText("Connected")).toBeInTheDocument();

    // user sends a message through the composer (Enter sends)
    const input = screen.getByPlaceholderText(/Ask about/i);
    fireEvent.change(input, { target: { value: "analyze example.com" } });
    fireEvent.keyDown(input, { key: "Enter", code: "Enter" });

    // the client framed and sent the message (session_id null -> server will create one)
    await waitFor(() => expect(liveSocket.sent.length).toBeGreaterThan(0));
    expect(liveSocket.sent[0]).toEqual({
      message: "analyze example.com",
      session_id: null,
    });

    // server turn: ack binds the session, then the streamed frames (all tagged with the session id
    // so the hook's real demux accepts them)
    act(() => {
      liveSocket.emit({ type: "ack", session_id: SESSION_ID });
      liveSocket.emit({ type: "start", session_id: SESSION_ID });
      liveSocket.emit({
        type: "status",
        session_id: SESSION_ID,
        tool: "analyze_observable",
      });
      liveSocket.emit({
        type: "action_required",
        session_id: SESSION_ID,
        pending_id: PENDING_ID,
        plan: PLAN,
      });
      liveSocket.emit({
        type: "token",
        session_id: SESSION_ID,
        content: "Prepared the plan.",
      });
      liveSocket.emit({
        type: "end",
        session_id: SESSION_ID,
        message_id: 1,
        content: "Prepared an analysis plan. Click Confirm.",
      });
    });

    // the M-1 confirm card is shown (persists past `end`); scope the observable lookup to the card
    // because "example.com" also appears in the echoed user message.
    expect(await screen.findByText("Start this analysis?")).toBeInTheDocument();
    const card = document.getElementById("chat-action-confirm");
    expect(within(card).getByText(/example\.com/)).toBeInTheDocument();

    // user confirms -> confirmAnalysis POST -> success message appended, card gone
    fireEvent.click(screen.getByRole("button", { name: "Confirm" }));

    expect(
      await screen.findByText(/Started analysis .* job #99 \(pending\)\./),
    ).toBeInTheDocument();
    expect(screen.queryByText("Start this analysis?")).not.toBeInTheDocument();
    expect(axios.post).toHaveBeenCalledTimes(1);
  });
});
