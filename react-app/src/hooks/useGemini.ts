/**
 * React hook for using Gemini service
 */

import { useState, useCallback } from 'react';
import { geminiService, type GeminiResponse, type ArticleAnalysis } from '../services/geminiService';

export interface UseGeminiReturn {
  summarizeArticle: (url: string) => Promise<void>;
  isLoading: boolean;
  result: ArticleAnalysis | null;
  error: string | null;
  isAvailable: boolean;
  reset: () => void;
}

export const useGemini = (): UseGeminiReturn => {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ArticleAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);

  const summarizeArticle = useCallback(async (url: string) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response: GeminiResponse = await geminiService.summarizeArticle(url);
      
      if (response.success && response.data) {
        setResult(response.data);
      } else {
        setError(response.error || 'Failed to summarize article');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    summarizeArticle,
    isLoading,
    result,
    error,
    isAvailable: geminiService.isAvailable(),
    reset
  };
};
