import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { SemanticSearchResult } from '@/types';
import { 
  getQualitsClassificationColor, 
  getQualitsBadgeColor, 
  formatSimilarityScore,
  QualitsClassification
} from '@/lib/utils';
import { highlightText } from '@/lib/textUtils';

interface SearchResultProps {
  // Props para busca normal
  title?: string;
  journal?: string;
  year?: number;
  issue?: string;
  abstract?: string;
  searchTerm: string;
  qualis?: QualitsClassification;
  authors?: string[];
  onClick?: () => void;
  
  // Props para busca semântica
  isSemanticSearch?: boolean;
  semanticResult?: SemanticSearchResult;
}

const SearchResult = ({ 
  // Busca normal
  title, 
  journal, 
  year, 
  issue, 
  abstract,
  searchTerm,
  qualis,
  authors = [],
  onClick,
  
  // Busca semântica
  isSemanticSearch = false,
  semanticResult
}: SearchResultProps) => {
  // Determina os dados a serem exibidos baseado no tipo de busca
  const displayData = isSemanticSearch && semanticResult ? {
    title: semanticResult.documento?.title || semanticResult.title || '',
    journal: semanticResult.documento?.journal || semanticResult.journal || '',
    year: semanticResult.documento?.year || semanticResult.year || 0,
    abstract: semanticResult.documento?.abstract || semanticResult.abstract || '',
    qualis: semanticResult.documento?.qualis || semanticResult.qualis,
    authors: semanticResult.documento?.authors || semanticResult.authors || [],
    score: semanticResult.score
  } : {
    title: title || '',
    journal: journal || '',
    year: year || 0,
    abstract: abstract || '',
    qualis,
    authors,
    score: undefined
  };

  const publicationInfo = [
    displayData.journal,
    displayData.year.toString(),
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
        {displayData.qualis && (
          <div className={`w-1 ${getQualitsClassificationColor(displayData.qualis)} flex-shrink-0`} />
        )}
        
        <CardContent className="p-6 flex-1">
          <div className="flex flex-col space-y-3">
            {/* Header com título e ano */}
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
              <h3 className="text-lg font-semibold leading-tight text-slate-800 hover:text-blue-600 transition-colors flex-1">
                {highlightText(displayData.title, searchTerm, isSemanticSearch)}
              </h3>
              <div className="flex gap-2 self-start">
                {/* Score de similaridade (apenas para busca semântica) */}
                {isSemanticSearch && displayData.score !== undefined && (
                  <div className="flex items-center space-x-2 bg-blue-50 px-2 py-1 rounded">
                    <div className="w-12 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-blue-400 to-blue-600 rounded-full transition-all duration-300"
                        style={{ width: `${displayData.score * 100}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium text-blue-600">
                      {formatSimilarityScore(displayData.score)}%
                    </span>
                  </div>
                )}
                {displayData.qualis && (
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getQualitsBadgeColor(displayData.qualis)}`}>
                    {displayData.qualis}
                  </span>
                )}
                <span className="px-2 py-1 rounded text-xs border border-slate-300 text-slate-600 bg-white">
                  {displayData.year}
                </span>
              </div>
            </div>
            {/* Autores do artigo */}
            {displayData.authors.length > 0 && (
              <div className="text-xs text-slate-500 mb-1">
                <span className="font-medium text-slate-600">Autores:</span> {
                  typeof displayData.authors[0] === 'string'
                    ? (displayData.authors as string[]).join(', ')
                    : (displayData.authors as Array<{ id: string; name: string }>).map(a => a.name).join(', ')
                }
              </div>
            )}
            {/* Informações da publicação */}
            <p className="text-sm text-slate-600">
              {publicationInfo}
            </p>
            
            {/* Abstract */}
            {displayData.abstract?.trim() && (
              <div className="text-sm text-slate-600 leading-relaxed">
                <p className="italic mb-1 text-slate-700">Abstract:</p>
                <p className="line-clamp-3">
                  {highlightText(displayData.abstract, searchTerm, isSemanticSearch)}
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </div>
    </Card>
  );
};

export default SearchResult;
