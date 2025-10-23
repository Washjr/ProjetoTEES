import { useState } from "react";
import { ApiService } from "@/services/apiService";
import { ArticleData, SemanticSearchResult } from "@/types";

export const useSearch = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [results, setResults] = useState<ArticleData[]>([]);
  const [semanticResults, setSemanticResults] = useState<SemanticSearchResult[]>([]);
  const [filterInterface, setFilterInterface] = useState<string>("");
  const [contentQuery, setContentQuery] = useState<string>("");

  const handleSearch = async (query: string) => {
    if (!query.trim()) return;

    setSearchTerm(query);
    setIsLoading(true);
    setHasSearched(true);

    try {
      const combinedResults = await ApiService.searchArticlesCombined(query);
      
      // Definir resultados da busca por termo
      setResults(combinedResults.termo_busca.resultados);
      
      // Definir resultados da busca semântica
      setSemanticResults(combinedResults.busca_semantica.resultados);
      
      // Armazenar informações da nova estrutura
      if ((combinedResults as any).structured_query?.filter_interface) {
        setFilterInterface((combinedResults as any).structured_query.filter_interface);
      } else {
        setFilterInterface("");
      }
      if ((combinedResults as any).structured_query?.content_query) {
        setContentQuery((combinedResults as any).structured_query.content_query);
      }
    } catch (error) {
      console.error("Erro na busca:", error);
      // Em caso de erro, limpar os resultados
      setResults([]);
      setSemanticResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const getTotalResults = () => {
    return results.length + semanticResults.length;
  };

  const hasResults = () => {
    return results.length > 0 || semanticResults.length > 0;
  };

  return {
    // States
    isLoading,
    hasSearched,
    searchTerm,
    results,
    semanticResults,
    filterInterface,
    contentQuery,
    
    // Actions
    handleSearch,
    getTotalResults,
    hasResults,
  };
};