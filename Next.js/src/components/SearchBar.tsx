
import React, { useRef, useLayoutEffect } from 'react';
import { Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SearchMode } from './SearchInterface';
import FilterTooltip from './FilterTooltip';

interface SearchBarProps {
  searchQuery: string;
  searchMode: SearchMode;
  onQueryChange: (query: string) => void;
  onKeyPress: (e: React.KeyboardEvent) => void;
  onSearch: () => void;
  isLoading?: boolean;
}

const SearchBar = ({ 
  searchQuery, 
  searchMode, 
  onQueryChange, 
  onKeyPress, 
  onSearch,
  isLoading = false
}: SearchBarProps) => {
  const placeholder = 'Ex: "artigos sobre inteligência artificial publicados em 2023"';

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useLayoutEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = '3.5rem';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [searchQuery]);

  const getIconColor = () => {
    if (!searchQuery) return 'text-slate-400 group-hover:text-slate-500';
    return searchMode === 'articles' ? 'text-blue-500' : 'text-indigo-500';
  };

  return (
    <div className="relative group">
      <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
        <Search 
          className={`h-5 w-5 transition-colors duration-200 ${getIconColor()}`} 
        />
      </div>
      <textarea
        ref={textareaRef}
        value={searchQuery}
        onInput={(e) => onQueryChange((e.target as HTMLTextAreaElement).value)}
        onKeyDown={onKeyPress}
        placeholder={placeholder}
        disabled={isLoading}
        rows={1}
        style={{ resize: 'none', minHeight: '3.5rem', maxHeight: '12rem', overflowY: 'auto', paddingTop: '0.9rem' }}
        className={`w-full pl-12 pr-40 text-lg bg-slate-50/80 border-2 rounded-xl transition-all duration-200 focus:outline-none focus:bg-white align-middle ${
          searchMode === 'articles'
            ? 'border-slate-200 focus:border-blue-400 focus:ring-4 focus:ring-blue-100'
            : 'border-slate-200 focus:border-indigo-400 focus:ring-4 focus:ring-indigo-100'
        } placeholder-slate-400 disabled:opacity-50 disabled:cursor-not-allowed`}
      />
      <div className="absolute inset-y-0 right-2 flex items-center space-x-2">
        <FilterTooltip />
        <Button
          onClick={onSearch}
          size="sm"
          disabled={isLoading || !searchQuery.trim()}
          className={`h-10 px-6 rounded-lg font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed ${
            searchMode === 'articles'
              ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl'
              : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg hover:shadow-xl'
          }`}
        >
          {isLoading ? 'Pesquisando...' : 'Pesquisar'}
        </Button>
      </div>
    </div>
  );
};

export default SearchBar;
