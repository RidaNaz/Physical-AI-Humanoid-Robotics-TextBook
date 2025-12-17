/**
 * API client for backend chat endpoints
 */

import type { ChatResponse, ChatError } from '@site/src/components/ChatWidget/types';

const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? 'https://ai-native-book-rho.vercel.app' // Deployed backend on Vercel
  : 'http://localhost:8000'; // Local FastAPI server

export class ChatAPI {
  /**
   * Send a query to the chat API
   */
  static async sendQuery(query: string): Promise<ChatResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        const errorData: ChatError = await response.json();
        throw new Error(errorData.error || 'Failed to get response');
      }

      const data: ChatResponse = await response.json();
      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  /**
   * Check API health
   */
  static async checkHealth(): Promise<{ status: string; qdrant: boolean; gemini: boolean }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/health`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Health check error:', error);
      return {
        status: 'error',
        qdrant: false,
        gemini: false,
      };
    }
  }
}
