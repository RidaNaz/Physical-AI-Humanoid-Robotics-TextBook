/**
 * Individual message bubble component
 */

import React from 'react';
import Link from '@docusaurus/Link';
import type { Message } from './types';
import styles from './styles.module.css';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={isUser ? styles.userMessage : styles.assistantMessage}>
      <div className={styles.messageContent}>
        {message.content}
      </div>

      {/* Show sources for assistant messages */}
      {!isUser && message.sources && message.sources.length > 0 && (
        <div className={styles.sources}>
          <div className={styles.sourcesLabel}>Sources:</div>
          {message.sources.map((source, idx) => (
            <Link
              key={idx}
              to={source.url}
              className={styles.sourceLink}
            >
              {source.title}
              {source.module && ` (${source.module})`}
            </Link>
          ))}
        </div>
      )}

      <div className={styles.messageTimestamp}>
        {new Date(message.timestamp).toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
        })}
      </div>
    </div>
  );
}
