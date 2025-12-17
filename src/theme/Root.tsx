/**
 * Docusaurus theme Root component
 * Injects ChatWidget globally across all pages
 */

import React, { ReactNode } from 'react';
import { ChatProvider } from '@site/src/components/ChatContext/ChatProvider';
import ChatWidget from '@site/src/components/ChatWidget';

interface RootProps {
  children: ReactNode;
}

export default function Root({ children }: RootProps): JSX.Element {
  return (
    <ChatProvider>
      {children}
      <ChatWidget />
    </ChatProvider>
  );
}
