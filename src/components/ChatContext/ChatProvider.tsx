/**
 * Chat Context Provider
 * Manages global chat state
 */

import React, { createContext, useState, useCallback, ReactNode } from 'react';
import type { ChatContextType, Message } from '@site/src/components/ChatWidget/types';
import { useChat } from '@site/src/hooks/useChat';
import { useLocalStorage } from '@site/src/hooks/useLocalStorage';

export const ChatContext = createContext<ChatContextType | undefined>(undefined);

interface ChatProviderProps {
  children: ReactNode;
}

const STORAGE_KEY = 'rag-chatbot-messages';
const MAX_STORED_MESSAGES = 50;

export function ChatProvider({ children }: ChatProviderProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [storedMessages, setStoredMessages] = useLocalStorage<Message[]>(STORAGE_KEY, []);

  const {
    messages,
    isLoading,
    error,
    sendMessage: sendMsg,
    clearMessages,
    setMessages,
    setError,
  } = useChat(storedMessages);

  // Persist messages to localStorage
  const persistMessages = useCallback((msgs: Message[]) => {
    // Keep only last N messages
    const recentMessages = msgs.slice(-MAX_STORED_MESSAGES);
    setStoredMessages(recentMessages);
  }, [setStoredMessages]);

  // Send message and persist
  const sendMessage = useCallback(async (content: string) => {
    await sendMsg(content);
    // Messages will be updated via useChat, then we persist
  }, [sendMsg]);

  // Persist messages whenever they change
  React.useEffect(() => {
    if (messages.length > 0) {
      persistMessages(messages);
    }
  }, [messages, persistMessages]);

  const clearHistory = useCallback(() => {
    clearMessages();
    setStoredMessages([]);
    setError(null);
  }, [clearMessages, setStoredMessages, setError]);

  const toggleChat = useCallback(() => {
    setIsOpen(prev => !prev);
  }, []);

  const contextValue: ChatContextType = {
    messages,
    isOpen,
    isLoading,
    error,
    sendMessage,
    clearHistory,
    toggleChat,
    setError,
  };

  return (
    <ChatContext.Provider value={contextValue}>
      {children}
    </ChatContext.Provider>
  );
}
