/**
 * Chat input field with send button
 */

import React, { useState, useRef, KeyboardEvent } from 'react';
import styles from './styles.module.css';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
}

const MAX_LENGTH = 500;

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmed = input.trim();
    if (trimmed && !disabled) {
      onSend(trimmed);
      setInput('');

      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);

    // Auto-resize textarea (max 5 lines)
    const textarea = e.target;
    textarea.style.height = 'auto';
    const maxHeight = 120; // ~5 lines
    textarea.style.height = Math.min(textarea.scrollHeight, maxHeight) + 'px';
  };

  const remainingChars = MAX_LENGTH - input.length;
  const isOverLimit = remainingChars < 0;

  return (
    <div className={styles.chatInputContainer}>
      <textarea
        ref={textareaRef}
        className={styles.chatInput}
        value={input}
        onChange={handleInput}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question about the book..."
        disabled={disabled}
        maxLength={MAX_LENGTH}
        rows={1}
      />

      <button
        className={styles.sendButton}
        onClick={handleSend}
        disabled={disabled || !input.trim() || isOverLimit}
        aria-label="Send message"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
        </svg>
      </button>

      {remainingChars < 50 && (
        <div className={`${styles.charCounter} ${isOverLimit ? styles.charCounterError : ''}`}>
          {remainingChars} characters remaining
        </div>
      )}
    </div>
  );
}
