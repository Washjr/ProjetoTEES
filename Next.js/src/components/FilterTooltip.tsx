import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Info } from 'lucide-react';

interface FilterTooltipProps {
  className?: string;
}

const FilterTooltip: React.FC<FilterTooltipProps> = ({ className = '' }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [filters, setFilters] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0, arrowLeft: 0 });
  const buttonRef = useRef<HTMLButtonElement>(null);

  const fetchFilters = async () => {
    if (filters.length > 0) return; // Já carregou os dados
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/self_query/');
      if (!response.ok) {
        throw new Error('Falha ao carregar filtros disponíveis');
      }
      const data = await response.json();
      setFilters(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
      console.error('Erro ao buscar filtros:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const updateTooltipPosition = () => {
    if (buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      const tooltipWidth = 320; // largura do tooltip (w-80 = 320px)
      
      // Calcula a posição ideal (centralizada)
      let left = rect.left + (rect.width / 2) - (tooltipWidth / 2);
      
      // Garante que o tooltip não saia da tela
      const margin = 16; // margem das bordas
      if (left < margin) {
        left = margin;
      } else if (left + tooltipWidth > window.innerWidth - margin) {
        left = window.innerWidth - tooltipWidth - margin;
      }
      
      // Posição da seta (sempre aponta para o centro do botão)
      const arrowLeft = Math.max(8, Math.min(tooltipWidth - 24, rect.left + (rect.width / 2) - left - 6));
      
      setTooltipPosition({
        top: rect.bottom + 8,
        left: left,
        arrowLeft: arrowLeft
      });
    }
  };

  const handleMouseEnter = () => {
    setIsVisible(true);
    fetchFilters();
    updateTooltipPosition();
  };

  const handleMouseLeave = () => {
    setIsVisible(false);
  };

  const handleClick = () => {
    if (!isVisible) {
      setIsVisible(true);
      fetchFilters();
      updateTooltipPosition();
    } else {
      setIsVisible(false);
    }
  };

  useEffect(() => {
    const handleResizeOrScroll = () => {
      if (isVisible) {
        updateTooltipPosition();
      }
    };

    window.addEventListener('resize', handleResizeOrScroll);
    window.addEventListener('scroll', handleResizeOrScroll);

    return () => {
      window.removeEventListener('resize', handleResizeOrScroll);
      window.removeEventListener('scroll', handleResizeOrScroll);
    };
  }, [isVisible]);

  const tooltipContent = (
    <div 
      className="w-80 bg-white border border-slate-200 rounded-lg shadow-2xl p-4 relative"
      role="tooltip"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={handleMouseLeave}
      style={{ 
        position: 'fixed',
        top: tooltipPosition.top,
        left: tooltipPosition.left,
        zIndex: 2147483647,
        maxHeight: '400px',
        overflowY: 'auto',
        overflow: 'visible'
      }}
    >
      <div className="mb-2">
        <h3 className="text-sm font-semibold text-slate-800">Filtros Disponíveis</h3>
      </div>
      
      {isLoading && (
        <div className="flex items-center justify-center py-4">
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-sm text-slate-600">Carregando...</span>
        </div>
      )}

      {error && (
        <div className="text-sm text-red-600 py-2">
          {error}
        </div>
      )}

      {!isLoading && !error && filters.length > 0 && (
        <div className="space-y-2">
          {filters.map((filter, index) => (
            <div key={`filter-${filter.slice(0, 20)}-${index}`} className="flex items-start space-x-2 text-sm">
              <span className="text-slate-400 mt-1.5 text-xs">•</span>
              <p className="text-slate-700 leading-relaxed">{filter}</p>
            </div>
          ))}
        </div>
      )}

      {!isLoading && !error && filters.length === 0 && (
        <div className="text-sm text-slate-500 py-2">
          Nenhum filtro disponível no momento.
        </div>
      )}

      {/* Seta do tooltip */}
      <div 
        className="absolute w-3 h-3 bg-white border-t border-l border-slate-200 transform rotate-45 -translate-x-1/2"
        style={{ 
          top: '-6px',
          left: `${tooltipPosition.arrowLeft}px`
        }}
      ></div>
    </div>
  );

  return (
    <div className={`relative inline-block ${className}`}>
      <button
        ref={buttonRef}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
        onFocus={handleMouseEnter}
        onBlur={handleMouseLeave}
        className="flex items-center justify-center w-8 h-8 rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-1 hover:opacity-80"
        style={{ backgroundColor: '#3e52e7' }}
        aria-label="Informações sobre filtros disponíveis"
        title="Clique para ver os filtros disponíveis"
      >
        <Info className="w-4 h-4 text-white" />
      </button>

      {isVisible && typeof document !== 'undefined' && createPortal(
        tooltipContent,
        document.body
      )}
    </div>
  );
};

export default FilterTooltip;