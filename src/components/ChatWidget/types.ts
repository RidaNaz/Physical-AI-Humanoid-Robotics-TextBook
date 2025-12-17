/**
 * TypeScript types and interfaces for chat widget
 */

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  sources?: Source[];
}

export interface Source {
  title: string;
  url: string;
  module: string;
  chapter?: string;
}

export interface ChatState {
  messages: Message[];
  isOpen: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface ChatContextType extends ChatState {
  sendMessage: (content: string) => Promise<void>;
  clearHistory: () => void;
  toggleChat: () => void;
  setError: (error: string | null) => void;
}

export interface ChatResponse {
  response: string;
  sources: Source[];
}

export interface ChatError {
  error: string;
  code: string;
}
