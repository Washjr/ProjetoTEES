
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface SearchResultProps {
  title: string;
  journal: string;
  year: number;
  volume?: string;
  issue?: string;
  abstractHighlight: string;
  searchTerm: string;
  onClick?: () => void;
}

const SearchResult = ({ 
  title, 
  journal, 
  year, 
  volume, 
  issue, 
  abstractHighlight, 
  searchTerm,
  onClick 
}: SearchResultProps) => {
  const highlightText = (text: string, term: string) => {
    if (!term) return text;
    
    const regex = new RegExp(`(${term})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <strong key={index} className="font-bold text-foreground">
          {part}
        </strong>
      ) : (
        part
      )
    );
  };

  const publicationInfo = [
    journal,
    year.toString(),
    volume && `Vol. ${volume}`,
    issue && `Issue ${issue}`
  ].filter(Boolean).join(', ');

  return (
    <Card 
      className={`w-full hover:shadow-md transition-all duration-200 border hover:border-primary/30 ${
        onClick ? 'cursor-pointer' : ''
      }`}
      onClick={onClick}
    >
      <CardContent className="p-6">
        <div className="flex flex-col space-y-3">
          {/* Header com título e ano */}
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
            <h3 className="text-lg font-semibold leading-tight hover:text-primary transition-colors flex-1">
              {title}
            </h3>
            <Badge variant="outline" className="text-xs self-start">
              {year}
            </Badge>
          </div>
          
          {/* Informações da publicação */}
          <p className="text-sm text-muted-foreground">
            {publicationInfo}
          </p>
          
          {/* Abstract */}
          <div className="text-sm text-muted-foreground leading-relaxed">
            <p className="italic mb-1">Abstract:</p>
            <p className="line-clamp-3">
              {highlightText(abstractHighlight, searchTerm)}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default SearchResult;
