import { useCallback, useMemo, useRef } from 'react';

/**
 * Custom hook for debouncing function calls
 */
export function useDebounce<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const timeoutRef = useRef<NodeJS.Timeout>();

  return useCallback(
    ((...args: Parameters<T>) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      timeoutRef.current = setTimeout(() => callback(...args), delay);
    }) as T,
    [callback, delay]
  );
}

/**
 * Custom hook for throttling function calls
 */
export function useThrottle<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const lastCall = useRef(0);
  const lastCallTimer = useRef<NodeJS.Timeout>();

  return useCallback(
    ((...args: Parameters<T>) => {
      const now = Date.now();
      if (now - lastCall.current >= delay) {
        callback(...args);
        lastCall.current = now;
      } else {
        if (lastCallTimer.current) {
          clearTimeout(lastCallTimer.current);
        }
        lastCallTimer.current = setTimeout(() => {
          callback(...args);
          lastCall.current = Date.now();
        }, delay - (now - lastCall.current));
      }
    }) as T,
    [callback, delay]
  );
}

/**
 * Memoized API call with caching
 */
export function useApiCache<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl: number = 5 * 60 * 1000 // 5 minutes
) {
  const cache = useRef<Map<string, { data: T; timestamp: number }>>(new Map());

  return useCallback(async (): Promise<T> => {
    const cached = cache.current.get(key);
    const now = Date.now();

    if (cached && now - cached.timestamp < ttl) {
      return cached.data;
    }

    const data = await fetcher();
    cache.current.set(key, { data, timestamp: now });
    return data;
  }, [key, fetcher, ttl]);
}

/**
 * Optimized list rendering with virtualization support
 */
export function useVirtualizedList<T>(
  items: T[],
  itemHeight: number,
  containerHeight: number
) {
  return useMemo(() => {
    const visibleCount = Math.ceil(containerHeight / itemHeight);
    const startIndex = 0;
    const endIndex = Math.min(startIndex + visibleCount, items.length);

    return {
      items: items.slice(startIndex, endIndex),
      startIndex,
      endIndex,
      totalHeight: items.length * itemHeight,
      offsetY: startIndex * itemHeight,
    };
  }, [items, itemHeight, containerHeight]);
}

/**
 * Performance monitoring hook
 */
export function usePerformanceMonitor(componentName: string) {
  const renderCount = useRef(0);
  const lastRenderTime = useRef(performance.now());

  renderCount.current += 1;
  const currentTime = performance.now();
  const renderTime = currentTime - lastRenderTime.current;
  lastRenderTime.current = currentTime;

  if (process.env.NODE_ENV === 'development') {
    console.log(`${componentName} rendered ${renderCount.current} times in ${renderTime.toFixed(2)}ms`);
  }

  return {
    renderCount: renderCount.current,
    renderTime,
  };
}

/**
 * Optimized image loading with lazy loading
 */
export function useImageLoader(src: string, placeholder?: string) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    const img = new Image();
    img.onload = () => setIsLoaded(true);
    img.onerror = () => setError(true);
    img.src = src;
  }, [src]);

  return {
    isLoaded,
    error,
    src: isLoaded ? src : placeholder,
  };
}

/**
 * Batch state updates for better performance
 */
export function useBatchUpdate<T>(initialState: T) {
  const [state, setState] = useState(initialState);
  const batchRef = useRef<Partial<T>>({});
  const timeoutRef = useRef<NodeJS.Timeout>();

  const batchSetState = useCallback((updates: Partial<T>) => {
    batchRef.current = { ...batchRef.current, ...updates };

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      setState(prev => ({ ...prev, ...batchRef.current }));
      batchRef.current = {};
    }, 16); // One frame at 60fps
  }, []);

  return [state, batchSetState] as const;
}

/**
 * Optimized scroll handling
 */
export function useScrollHandler(
  handler: (event: Event) => void,
  throttleMs: number = 16
) {
  const throttledHandler = useThrottle(handler, throttleMs);

  useEffect(() => {
    window.addEventListener('scroll', throttledHandler, { passive: true });
    return () => window.removeEventListener('scroll', throttledHandler);
  }, [throttledHandler]);
}

/**
 * Memory-efficient string search
 */
export function useStringSearch<T>(
  items: T[],
  searchTerm: string,
  getSearchableText: (item: T) => string
) {
  return useMemo(() => {
    if (!searchTerm.trim()) return items;

    const term = searchTerm.toLowerCase();
    return items.filter(item => 
      getSearchableText(item).toLowerCase().includes(term)
    );
  }, [items, searchTerm, getSearchableText]);
}

/**
 * Optimized form validation
 */
export function useFormValidation<T extends Record<string, any>>(
  initialValues: T,
  validationSchema: Record<keyof T, (value: any) => string | null>
) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});
  const [isValid, setIsValid] = useState(true);

  const validate = useCallback((newValues: T) => {
    const newErrors: Partial<Record<keyof T, string>> = {};
    let valid = true;

    Object.keys(validationSchema).forEach(key => {
      const error = validationSchema[key as keyof T](newValues[key]);
      if (error) {
        newErrors[key as keyof T] = error;
        valid = false;
      }
    });

    setErrors(newErrors);
    setIsValid(valid);
    return valid;
  }, [validationSchema]);

  const setValue = useCallback((key: keyof T, value: any) => {
    const newValues = { ...values, [key]: value };
    setValues(newValues);
    validate(newValues);
  }, [values, validate]);

  return {
    values,
    errors,
    isValid,
    setValue,
    setValues: useCallback((newValues: T) => {
      setValues(newValues);
      validate(newValues);
    }, [validate]),
  };
}

// Import useState and useEffect for the hooks above
import { useState, useEffect } from 'react'; 