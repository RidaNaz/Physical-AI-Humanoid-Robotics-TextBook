/**
 * Expandable chat panel container
 */

import React from 'react';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { useChatContext } from '../ChatContext/useChatContext';
import styles from './styles.module.css';

export function ChatPanel() {
  const { messages, isLoading, toggleChat, sendMessage, clearHistory, isOpen } = useChatContext();

  if (!isOpen) return null;

  return (
    <div className={styles.chatPanel}>
      {/* Header */}
      <div className={styles.chatHeader}>
        <div className={styles.chatHeaderTitle}>
          <span className={styles.chatHeaderIcon}>🤖</span>
          <span>AI Assistant</span>
        </div>

        <div className={styles.chatHeaderActions}>
          {messages.length > 0 && (
            <button
              className={styles.clearButton}
              onClick={clearHistory}
              aria-label="Clear chat history"
              title="Clear chat history"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="3 6 5 6 21 6" />
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
              </svg>
            </button>
          )}

          <button
            className={styles.closeButton}
            onClick={toggleChat}
            aria-label="Close chat"
            title="Close chat"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
      </div>

      {/* Messages */}
      <MessageList messages={messages} isLoading={isLoading} />

      {/* Input */}
      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}
