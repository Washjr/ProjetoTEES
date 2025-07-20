import React from "react";
import { Card, CardContent } from '@/components/ui/card';
import { SemanticSearchResult } from "@/types";

interface SemanticSearchResultProps {
  result: SemanticSearchResult;
  searchTerm: string;
  onClick: () => void;
}

const SemanticSearchResultComponent: React.FC<SemanticSearchResultProps> = ({
  result,
  searchTerm,
  onClick,
}) => {
  const { documento, score } = result;

  const highlightText = (text: string, searchTerm: string) => {
    if (!searchTerm) return text;
    
    const regex = new RegExp(`(${searchTerm})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <span key={index} className="bg-yellow-200 font-medium">
          {part}
        </span>
      ) : (
        part
      )
    );
  };

  const getQualitsColor = (qualis?: string) => {
    switch (qualis?.toUpperCase()) {
      case 'A1': return 'bg-green-600 text-white';
      case 'A2': return 'bg-green-500 text-white';
      case 'A3': return 'bg-green-400 text-white';
      case 'A4': return 'bg-green-300 text-gray-800';
      case 'B1': return 'bg-orange-600 text-white';
      case 'B2': return 'bg-orange-500 text-white';
      case 'B3': return 'bg-orange-400 text-gray-800';
      case 'B4': return 'bg-orange-300 text-gray-800';
      case 'C': return 'bg-red-500 text-white';
      case 'SQ': return 'bg-gray-400 text-white';
      default: return 'bg-gray-300 text-gray-800';
    }
  };

  const getQualitsSidebarColor = (qualis?: string) => {
    switch (qualis?.toUpperCase()) {
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

  const formatScore = (score: number) => {
    return (score * 100).toFixed(1);
  };

  return (
    <Card 
      className="w-full hover:shadow-md transition-all duration-200 border-slate-200/50 bg-white/70 backdrop-blur-sm hover:border-blue-300/50 overflow-hidden cursor-pointer hover:bg-white/90"
      onClick={onClick}
    >
      <div className="flex">
        {/* Barra lateral colorida para classificação Qualis */}
        {documento.qualis && (
          <div className={`w-1 ${getQualitsSidebarColor(documento.qualis)} flex-shrink-0`} />
        )}
        
        <CardContent className="p-6 flex-1">
          <div className="flex flex-col space-y-3">
            {/* Header com título e badges */}
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
              <h3 className="text-lg font-semibold leading-tight text-slate-800 hover:text-blue-600 transition-colors flex-1">
                {highlightText(documento.title, searchTerm)}
              </h3>
              <div className="flex gap-2 self-start">
                {/* Score de similaridade */}
                <div className="flex items-center space-x-2 bg-blue-50 px-2 py-1 rounded">
                  <div className="w-12 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-blue-400 to-blue-600 rounded-full transition-all duration-300"
                      style={{ width: `${score * 100}%` }}
                    />
                  </div>
                  <span className="text-xs font-medium text-blue-600">
                    {formatScore(score)}%
                  </span>
                </div>
                {documento.qualis && (
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getQualitsColor(documento.qualis)}`}>
                    {documento.qualis}
                  </span>
                )}
                <span className="px-2 py-1 rounded text-xs border border-slate-300 text-slate-600 bg-white">
                  {documento.year}
                </span>
              </div>
            </div>
            
            {/* Informações da publicação */}
            <p className="text-sm text-slate-600">
              {documento.journal}
            </p>

            {/* Abstract (se disponível) */}
            {documento.abstract && documento.abstract.trim() && (
              <div className="text-sm text-slate-600 leading-relaxed">
                <p className="italic mb-1 text-slate-700">Abstract:</p>
                <p className="overflow-hidden" style={{
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical'
                }}>
                  {highlightText(documento.abstract, searchTerm)}
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </div>
    </Card>
  );
};

export default SemanticSearchResultComponent;
