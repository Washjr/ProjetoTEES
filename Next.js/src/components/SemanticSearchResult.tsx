import React from "react";
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
      case 'B1': return 'bg-blue-500 text-white';
      case 'B2': return 'bg-blue-400 text-white';
      case 'B3': return 'bg-blue-300 text-gray-800';
      case 'B4': return 'bg-blue-200 text-gray-800';
      case 'C': return 'bg-yellow-400 text-gray-800';
      default: return 'bg-gray-300 text-gray-800';
    }
  };

  const formatScore = (score: number) => {
    return (score * 100).toFixed(1);
  };

  return (
    <div 
      className="bg-white rounded-lg border border-slate-200 p-6 hover:shadow-md transition-shadow cursor-pointer hover:border-blue-300"
      onClick={onClick}
    >
      {/* Header com score de similaridade */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <span className="text-sm text-slate-500">Similaridade:</span>
          <div className="flex items-center space-x-2">
            <div className="w-20 h-2 bg-slate-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-blue-400 to-blue-600 rounded-full transition-all duration-300"
                style={{ width: `${score * 100}%` }}
              />
            </div>
            <span className="text-sm font-medium text-blue-600">
              {formatScore(score)}%
            </span>
          </div>
        </div>
        
        {/* Qualis badge */}
        {documento.qualis && (
          <span className={`px-2 py-1 rounded text-xs font-medium ${getQualitsColor(documento.qualis)}`}>
            {documento.qualis}
          </span>
        )}
      </div>

      {/* Título do artigo */}
      <h3 className="text-lg font-semibold text-slate-800 mb-2 leading-tight hover:text-blue-600 transition-colors">
        {highlightText(documento.title, searchTerm)}
      </h3>

      {/* Informações do periódico e ano */}
      <div className="flex items-center space-x-3 text-sm text-slate-600 mb-3">
        <span className="font-medium">{documento.journal}</span>
        <span className="text-slate-400">•</span>
        <span>{documento.year}</span>
      </div>

      {/* Autores */}
      <div className="mb-4">
        <p className="text-sm text-slate-600">
          <span className="font-medium">Autores:</span>{" "}
          {documento.authors.map((author, index) => (
            <span key={author.id}>
              {author.name}
              {index < documento.authors.length - 1 && ", "}
            </span>
          ))}
        </p>
      </div>

      {/* Abstract (se disponível) */}
      {documento.abstract && documento.abstract.trim() && (
        <p className="text-sm text-slate-700 leading-relaxed overflow-hidden" style={{
          display: '-webkit-box',
          WebkitLineClamp: 3,
          WebkitBoxOrient: 'vertical'
        }}>
          {highlightText(documento.abstract, searchTerm)}
        </p>
      )}

      {/* DOI (se disponível) */}
      {documento.doi && (
        <div className="mt-3 pt-3 border-t border-slate-100">
          <p className="text-xs text-slate-500">
            <span className="font-medium">DOI:</span> {documento.doi}
          </p>
        </div>
      )}
    </div>
  );
};

export default SemanticSearchResultComponent;
