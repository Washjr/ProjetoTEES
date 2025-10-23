import { useState, useEffect } from "react";

interface UsePaginationProps {
  totalResults: number;
  itemsPerPage?: number;
}

export const usePagination = ({ totalResults, itemsPerPage = 10 }: UsePaginationProps) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    const calculatedTotalPages = Math.ceil(totalResults / itemsPerPage);
    setTotalPages(calculatedTotalPages);
    
    // Reset to first page if current page exceeds total pages
    if (currentPage > calculatedTotalPages && calculatedTotalPages > 0) {
      setCurrentPage(1);
    }
  }, [totalResults, itemsPerPage, currentPage]);

  const resetPagination = () => {
    setCurrentPage(1);
  };

  return {
    // States
    currentPage,
    totalPages,
    
    // Actions
    setCurrentPage,
    resetPagination,
  };
};