import React from "react";

/**
 * Destaca texto baseado em um termo de busca
 * @param text - Texto a ser destacado
 * @param term - Termo de busca
 * @param isSemanticSearch - Se é busca semântica (muda o estilo do destaque)
 * @returns Texto com partes destacadas
 */
export function highlightText(text: string, term: string, isSemanticSearch: boolean = false): React.ReactNode {
  if (!term) return text;
  
  const regex = new RegExp(`(${term})`, 'gi');
  const parts = text.split(regex);
  
  return parts.map((part, partIndex) => 
    regex.test(part) ? (
      <span 
        key={`${term}-${part}-${partIndex}`} 
        className={isSemanticSearch ? "bg-yellow-200 font-medium" : "font-bold text-blue-700"}
      >
        {part}
      </span>
    ) : (
      part
    )
  );
}