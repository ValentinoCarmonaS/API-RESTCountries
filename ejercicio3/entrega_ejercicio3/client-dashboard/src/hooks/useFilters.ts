import { useState, useCallback } from 'react';
import type { SalesFilters } from '../types/types';

export const useFilters = () => {
  const [filters, setFilters] = useState<SalesFilters>({
    dateRange: {
      start: null,
      end: null
    },
    selectedProduct: null
  });

  const setDateRangeStart = useCallback((date: Date | null) => {
    setFilters(prev => ({
      ...prev,
      dateRange: {
        ...prev.dateRange,
        start: date
      }
    }));
  }, []);

  const setDateRangeEnd = useCallback((date: Date | null) => {
    setFilters(prev => ({
      ...prev,
      dateRange: {
        ...prev.dateRange,
        end: date
      }
    }));
  }, []);

  const setSelectedProduct = useCallback((product: string | null) => {
    setFilters(prev => ({
      ...prev,
      selectedProduct: product
    }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({
      dateRange: {
        start: null,
        end: null
      },
      selectedProduct: null
    });
  }, []);

  const hasActiveFilters = Boolean(
    filters.dateRange.start ||
    filters.dateRange.end ||
    filters.selectedProduct
  );

  return {
    filters,
    setDateRangeStart,
    setDateRangeEnd,
    setSelectedProduct,
    clearFilters,
    hasActiveFilters
  };
};
