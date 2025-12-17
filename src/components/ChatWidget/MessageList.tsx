/**
 * Scrollable list of messages
 */

import React, { useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import { LoadingIndicator } from './LoadingIndicator';
import type { Message } from './types';
import styles from './styles.module.css';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className={styles.messageList}>
      {messages.length === 0 && (
        <div className={styles.emptyState}>
          <h3>👋 Hi! I'm your AI assistant</h3>
          <p>Ask me anything about Physical AI & Humanoid Robotics!</p>
          <div className={styles.suggestedQuestions}>
            <p><strong>Try asking:</strong></p>
            <ul>
              <li>"What is ROS 2?"</li>
              <li>"Explain NVIDIA Isaac"</li>
              <li>"What are Vision-Language-Action models?"</li>
            </ul>
          </div>
        </div>
      )}

      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {isLoading && (
        <div className={styles.assistantMessage}>
          <LoadingIndicator />
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
