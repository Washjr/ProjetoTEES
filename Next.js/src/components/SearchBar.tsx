
import React from 'react';
import { Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SearchMode } from './SearchInterface';

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
  const placeholder = searchMode === 'articles' 
    ? 'Pesquisar artigos, publicações, trabalhos...'
    : 'Pesquisar pesquisadores, professores, autores...';

  return (
    <div className="relative group">
      <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
        <Search 
          className={`h-5 w-5 transition-colors duration-200 ${
            searchQuery 
              ? (searchMode === 'articles' ? 'text-blue-500' : 'text-indigo-500')
              : 'text-slate-400 group-hover:text-slate-500'
          }`} 
        />
      </div>
      
      <input
        type="text"
        value={searchQuery}
        onChange={(e) => onQueryChange(e.target.value)}
        onKeyPress={onKeyPress}
        placeholder={placeholder}
        disabled={isLoading}
        className={`w-full h-14 pl-12 pr-24 text-lg bg-slate-50/80 border-2 rounded-xl transition-all duration-200 focus:outline-none focus:bg-white ${
          searchMode === 'articles'
            ? 'border-slate-200 focus:border-blue-400 focus:ring-4 focus:ring-blue-100'
            : 'border-slate-200 focus:border-indigo-400 focus:ring-4 focus:ring-indigo-100'
        } placeholder-slate-400 disabled:opacity-50 disabled:cursor-not-allowed`}
      />
      
      <div className="absolute inset-y-0 right-2 flex items-center">
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
