/**
 * Main ChatWidget component
 * Combines ChatButton and ChatPanel
 */

import React from 'react';
import { ChatButton } from './ChatButton';
import { ChatPanel } from './ChatPanel';
import { useChatContext } from '../ChatContext/useChatContext';
import styles from './styles.module.css';

export default function ChatWidget() {
  const { isOpen, toggleChat } = useChatContext();

  return (
    <div className={styles.chatWidget}>
      <ChatPanel />
      <ChatButton onClick={toggleChat} isOpen={isOpen} />
    </div>
  );
}
