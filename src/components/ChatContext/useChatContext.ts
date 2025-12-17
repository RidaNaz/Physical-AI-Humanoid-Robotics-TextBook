/**
 * Hook to access Chat Context
 */

import { useContext } from 'react';
import { ChatContext } from './ChatProvider';
import type { ChatContextType } from '@site/src/components/ChatWidget/types';

export function useChatContext(): ChatContextType {
  const context = useContext(ChatContext);

  if (context === undefined) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }

  return context;
}
