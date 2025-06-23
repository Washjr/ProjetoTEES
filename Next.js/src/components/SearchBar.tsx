
import React from 'react';
import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface SearchBarProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  onSearch: () => void;
  isLoading: boolean;
  searchType: 'artigo' | 'pesquisador';
  onSearchTypeChange: (type: 'artigo' | 'pesquisador') => void;
}

const SearchBar = ({ 
  searchTerm, 
  onSearchChange, 
  onSearch, 
  isLoading, 
  searchType, 
  onSearchTypeChange 
}: SearchBarProps) => {
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      onSearch();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="relative flex items-center gap-2">
        <Select value={searchType} onValueChange={onSearchTypeChange}>
          <SelectTrigger className="w-[140px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="artigo">Artigo</SelectItem>
            <SelectItem value="pesquisador">Pesquisador</SelectItem>
          </SelectContent>
        </Select>
        
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
          <Input
            type="text"
            placeholder="Digite sua pesquisa..."
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            onKeyPress={handleKeyPress}
            className="pl-10 pr-4 py-3 text-base"
            disabled={isLoading}
          />
        </div>
        <Button 
          onClick={onSearch} 
          disabled={isLoading || !searchTerm.trim()}
          className="px-6 py-3"
        >
          {isLoading ? 'Buscando...' : 'Buscar'}
        </Button>
      </div>
    </div>
  );
};

export default SearchBar;
