
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface SearchResultProps {
  title: string;
  journal: string;
  year: number;
  issue?: string;
  abstract: string;
  searchTerm: string;
  qualis?: 'A1' | 'A2' | 'A3' | 'A4' | 'B1' | 'B2' | 'B3' | 'B4' | 'C' | 'SQ';
  onClick?: () => void;
}

const SearchResult = ({ 
  title, 
  journal, 
  year, 
  issue, 
  abstract,
  searchTerm,
  qualis,
  onClick 
}: SearchResultProps) => {
  const highlightText = (text: string, term: string) => {
    if (!term) return text;
    
    const regex = new RegExp(`(${term})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <strong key={index} className="font-bold text-blue-700">
          {part}
        </strong>
      ) : (
        part
      )
    );
  };

  const getClassificationColor = (classification?: string) => {
    switch (classification) {
      case 'A1': return 'bg-green-600';
      case 'A2': return 'bg-green-500';
      case 'A3': return 'bg-green-400';
      case 'A4': return 'bg-green-300';
      case 'B1': return 'bg-orange-600';
      case 'B2': return 'bg-orange-500';
      case 'B3': return 'bg-orange-400';
      case 'B4': return 'bg-orange-300';
      case 'C': return 'bg-red-500';
      case 'SQ': return 'bg-gray-400';
      default: return 'bg-transparent';
    }
  };

  const publicationInfo = [
    journal,
    year.toString(),
    issue && `Issue ${issue}`
  ].filter(Boolean).join(', ');

  return (
    <Card 
      className={`w-full hover:shadow-md transition-all duration-200 border-slate-200/50 bg-white/70 backdrop-blur-sm hover:border-blue-300/50 overflow-hidden ${
        onClick ? 'cursor-pointer hover:bg-white/90' : ''
      }`}
      onClick={onClick}
    >
      <div className="flex">
        {/* Barra lateral colorida para classificação */}
        {qualis && (
          <div className={`w-1 ${getClassificationColor(qualis)} flex-shrink-0`} />
        )}
        
        <CardContent className="p-6 flex-1">
          <div className="flex flex-col space-y-3">
            {/* Header com título e ano */}
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
              <h3 className="text-lg font-semibold leading-tight text-slate-800 hover:text-blue-600 transition-colors flex-1">
                {title}
              </h3>
              <div className="flex gap-2 self-start">
                {qualis && (
                  <Badge variant="secondary" className="text-xs bg-blue-100 text-blue-700 hover:bg-blue-200">
                    {qualis}
                  </Badge>
                )}
                <Badge variant="outline" className="text-xs border-slate-300 text-slate-600">
                  {year}
                </Badge>
              </div>
            </div>
            
            {/* Informações da publicação */}
            <p className="text-sm text-slate-600">
              {publicationInfo}
            </p>
            
            {/* Abstract */}
            <div className="text-sm text-slate-600 leading-relaxed">
              <p className="italic mb-1 text-slate-700">Abstract:</p>
              <p className="line-clamp-3">
                {highlightText(abstract, searchTerm)}
              </p>
            </div>
          </div>
        </CardContent>
      </div>
    </Card>
  );
};

export default SearchResult;
