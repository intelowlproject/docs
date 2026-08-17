import React from "react";
import PropTypes from "prop-types";
import { Button, ListGroup, ListGroupItem, Spinner, Alert } from "reactstrap";
import { IoAdd, IoTrashOutline } from "react-icons/io5";
import { format } from "date-fns-tz";

import { useChatStore, deriveSessionLabel } from "../../stores/useChatStore";
import { areYouSureConfirmDialog } from "../common/areYouSureConfirmDialog";

/**
 * The sessions view of the chat drawer (master-detail counterpart of the conversation view). Lists
 * the user's conversations with a backend-provided title + creation time, lets them start a new
 * chat, switch to an existing one, or delete one. `onSessionChosen` flips the parent panel back to
 * the conversation view after a switch/new.
 *
 * Switching/new are allowed while a turn streams: the store bumps navEpoch to abandon the in-flight
 * turn (see useChatStore). Delete is still blocked for the active-streaming session (the server is
 * persisting that session's messages). The WebSocket hook is untouched—it reads the bound sessionId
 * live.
 */
export function ChatSessionList({ onSessionChosen }) {
  const sessions = useChatStore((state) => state.sessions);
  const loading = useChatStore((state) => state.sessionsLoading);
  const error = useChatStore((state) => state.sessionsError);
  const sessionId = useChatStore((state) => state.sessionId);
  const fetchSessions = useChatStore((state) => state.fetchSessions);
  const switchSession = useChatStore((state) => state.switchSession);
  const newChat = useChatStore((state) => state.newChat);
  const deleteSession = useChatStore((state) => state.deleteSession);

  // Refetch every time the list is shown so deletes/new sessions from other tabs are reflected.
  React.useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  const handleSelect = (id) => {
    switchSession(id);
    onSessionChosen();
  };

  const handleNew = () => {
    newChat();
    onSessionChosen();
  };

  const handleDelete = async (id) => {
    const sure = await areYouSureConfirmDialog("delete this conversation");
    if (sure) deleteSession(id);
  };

  return (
    <div
      className="d-flex flex-column overflow-auto p-2"
      id="chat-session-list"
    >
      <Button color="primary" className="mb-2" onClick={handleNew}>
        <IoAdd className="me-1" /> New chat
      </Button>
      {error && (
        <Alert color="danger" className="m-0 mb-2">
          {error}
        </Alert>
      )}
      {loading && (
        <div className="text-center p-3">
          <Spinner size="sm" />
        </div>
      )}
      {!loading && !error && sessions.length === 0 && (
        <div className="text-muted text-center p-3">No conversations yet.</div>
      )}
      <ListGroup flush>
        {sessions.map((session) => (
          <ListGroupItem
            key={session.id}
            tag="button"
            type="button"
            action
            active={session.id === sessionId}
            onClick={() => handleSelect(session.id)}
            className="d-flex justify-content-between align-items-center"
          >
            <div className="text-truncate">
              <div className="text-truncate">{deriveSessionLabel(session)}</div>
              <small className="text-muted">
                {format(new Date(session.created_at), "yyyy-MM-dd HH:mm")}
              </small>
            </div>
            {/* A <button> nested in the tag="button" row is invalid HTML, so the delete control is a
                role="button" span that stops propagation to avoid also triggering the row switch. */}
            <span
              role="button"
              tabIndex={0}
              aria-label="Delete conversation"
              className="ms-2 text-danger"
              onClick={(event) => {
                event.stopPropagation();
                handleDelete(session.id);
              }}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.stopPropagation();
                  handleDelete(session.id);
                }
              }}
            >
              <IoTrashOutline />
            </span>
          </ListGroupItem>
        ))}
      </ListGroup>
    </div>
  );
}

ChatSessionList.propTypes = {
  onSessionChosen: PropTypes.func.isRequired,
};
