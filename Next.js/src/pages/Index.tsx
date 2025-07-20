import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import SearchInterface, { SearchMode } from "@/components/SearchInterface";
import SearchSummary from "@/components/SearchSummary";
import SearchResult from "@/components/SearchResult";
import SemanticSearchResultComponent from "@/components/SemanticSearchResult";
import SearchSectionDivider from "@/components/SearchSectionDivider";
import LoadingSpinner from "@/components/LoadingSpinner";
import NoResults from "@/components/NoResults";
import ResearcherCard from "@/components/ResearcherCard";
import ArticleOverlay from "@/components/ArticleOverlay";
import SearchPagination from "@/components/SearchPagination";
import { ApiService } from "@/services/apiService";
import { ArticleData, ResearcherData, CombinedSearchData, SemanticSearchResult } from "@/types";

const Index = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [searchMode, setSearchMode] = useState<SearchMode>("articles");
  const [results, setResults] = useState<ArticleData[]>([]);
  const [semanticResults, setSemanticResults] = useState<SemanticSearchResult[]>([]);
  const [researchers, setResearchers] = useState<ResearcherData[]>([]);
  const [aiSummary, setAiSummary] = useState<string>("");
  const [tags, setTags] = useState<string[]>([]);
  const [selectedArticle, setSelectedArticle] =
    useState<ArticleData | null>(null);
  const [isOverlayOpen, setIsOverlayOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const handleSearch = async (query: string, mode: SearchMode) => {
    if (!query.trim()) return;

    setSearchTerm(query);
    setSearchMode(mode);
    setIsLoading(true);
    setHasSearched(true);
    setCurrentPage(1);

    try {
      if (mode === "articles") {
        const combinedResults = await ApiService.searchArticlesCombined(query);
        
        // Definir resultados da busca por termo
        setResults(combinedResults.termo_busca.resultados);
        setAiSummary(combinedResults.termo_busca.resumo_ia);
        setTags(combinedResults.termo_busca.tags || []);
        
        // Definir resultados da busca semântica
        setSemanticResults(combinedResults.busca_semantica.resultados);
        
        // Limpar dados de pesquisadores
        setResearchers([]);
        
        // Calcular paginação baseada nos resultados totais
        const totalResults = combinedResults.termo_busca.resultados.length + combinedResults.busca_semantica.resultados.length;
        setTotalPages(Math.ceil(totalResults / 10));
      } else {
        const searchResearchers = await ApiService.searchResearchers(query);
        setResearchers(searchResearchers);
        setResults([]);
        setSemanticResults([]);
        setAiSummary("");
        setTags([]);
        setTotalPages(Math.ceil(searchResearchers.length / 8));
      }
    } catch (error) {
      console.error("Erro na busca:", error);
      // Em caso de erro, limpar os resultados
      setResults([]);
      setSemanticResults([]);
      setResearchers([]);
      setAiSummary("");
      setTags([]);
      setTotalPages(1);
    } finally {
      setIsLoading(false);
    }
  };

  const handleArticleClick = (article: ArticleData) => {
    setSelectedArticle(article);
    setIsOverlayOpen(true);
  };

  const handleSemanticResultClick = (semanticResult: SemanticSearchResult) => {
    setSelectedArticle(semanticResult.documento);
    setIsOverlayOpen(true);
  };

  const handleAuthorClick = (authorId: string) => {
    setIsOverlayOpen(false);
    navigate(`/researcher/${authorId}`);
  };

  const handleResearcherClick = (researcherId: string) => {
    navigate(`/researcher/${researcherId}`);
  };

  const handleLogoClick = () => {
    // Limpar todos os estados da pesquisa
    setHasSearched(false);
    setSearchTerm("");
    setResults([]);
    setSemanticResults([]);
    setResearchers([]);
    setAiSummary("");
    setTags([]);
    setCurrentPage(1);
    setTotalPages(1);
    setIsLoading(false);
    setSelectedArticle(null);
    setIsOverlayOpen(false);
    // Navegar para a página inicial
    navigate('/');
  };

  const getTotalResults = () =>
    searchMode === "articles" ? results.length + semanticResults.length : researchers.length;
  const getTopKeyword = () => {
    if (searchTerm.toLowerCase().includes("machine")) return "algoritmos";
    if (searchTerm.toLowerCase().includes("climate")) return "temperatura";
    return "pesquisa";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header simples */}
      <header className="border-b border-slate-200/50 bg-white/70 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div 
              className="flex items-center space-x-3 cursor-pointer hover:opacity-80 transition-opacity"
              onClick={handleLogoClick}
            >
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">AE</span>
              </div>
              <span className="font-semibold text-slate-800">
                Pesquisa Acadêmica
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Seção de busca centralizada */}
        <div
          className={`transition-all duration-500 ${
            hasSearched
              ? "mb-8 flex justify-center"
              : "min-h-[60vh] flex items-center justify-center"
          }`}
        >
          <div className={`w-full ${hasSearched ? "max-w-2xl" : "max-w-4xl"}`}>
            {!hasSearched && (
              <div className="max-w-4xl mx-auto text-center mb-12">
                <h1 className="text-5xl font-bold text-slate-800 mb-4 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  Pesquisa Acadêmica
                </h1>
                <p className="text-xl text-slate-600 mb-2">
                  Descubra pesquisas inovadoras e conecte-se com acadêmicos
                  líderes
                </p>
                <p className="text-lg text-slate-500">
                  Pesquise entre artigos e perfis de pesquisadores
                </p>
              </div>
            )}

            <SearchInterface onSearch={handleSearch} isLoading={isLoading} />

            {!hasSearched && (
              <div className="mt-16 grid md:grid-cols-3 gap-8 max-w-3xl mx-auto">
                <div className="text-center p-6 bg-white/70 backdrop-blur-sm rounded-xl border border-slate-200/50 shadow-sm hover:shadow-md transition-shadow">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg mx-auto mb-4 flex items-center justify-center">
                    <span className="text-blue-600 text-xl font-semibold">
                      📚
                    </span>
                  </div>
                  <h3 className="font-semibold text-slate-800 mb-2">
                    Artigos de Pesquisa
                  </h3>
                  <p className="text-sm text-slate-600">
                    Artigos de professores da Universidade do Estado da Bahia
                  </p>
                </div>

                <div className="text-center p-6 bg-white/70 backdrop-blur-sm rounded-xl border border-slate-200/50 shadow-sm hover:shadow-md transition-shadow">
                  <div className="w-12 h-12 bg-indigo-100 rounded-lg mx-auto mb-4 flex items-center justify-center">
                    <span className="text-indigo-600 text-xl font-semibold">
                      👨‍🎓
                    </span>
                  </div>
                  <h3 className="font-semibold text-slate-800 mb-2">
                    Professores
                  </h3>
                  <p className="text-sm text-slate-600">
                    Visualize dados de professores e pesquisadores
                  </p>
                </div>

                <div className="text-center p-6 bg-white/70 backdrop-blur-sm rounded-xl border border-slate-200/50 shadow-sm hover:shadow-md transition-shadow">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg mx-auto mb-4 flex items-center justify-center">
                    <span className="text-purple-600 text-xl font-semibold">
                      🔬
                    </span>
                  </div>
                  <h3 className="font-semibold text-slate-800 mb-2">
                    Últimas Pesquisas
                  </h3>
                  <p className="text-sm text-slate-600">
                    Fique atualizado com as recentes pesquisas dos professores
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Resultados da busca */}
        {hasSearched && (
          <div className="max-w-6xl mx-auto">
            {isLoading ? (
              <LoadingSpinner />
            ) : (
              <>
                {/* Sumário apenas para artigos */}
                {searchMode === "articles" && results.length > 0 && (
                  <SearchSummary
                    totalResults={getTotalResults()}
                    topKeyword={getTopKeyword()}
                    searchTerm={searchTerm}
                    aiSummary={aiSummary}
                    tags={tags}
                  />
                )}

                {/* Resultados */}
                {searchMode === "articles" ? (
                  (results.length > 0 || semanticResults.length > 0) ? (
                    <div className="space-y-6">
                      {/* Resultados por termo */}
                      {results.length > 0 && (
                        <>
                          <SearchSectionDivider 
                            title="Busca por Termo" 
                            count={results.length}
                            icon="🔤"
                          />
                          <div className="space-y-4">
                            {results.map((result) => (
                              <SearchResult
                                key={result.id}
                                title={result.title}
                                journal={result.journal}
                                year={result.year}
                                qualis={result.qualis}
                                abstract={result.abstract}
                                searchTerm={searchTerm}
                                onClick={() => handleArticleClick(result)}
                              />
                            ))}
                          </div>
                        </>
                      )}

                      {/* Resultados semânticos */}
                      {semanticResults.length > 0 && (
                        <>
                          <SearchSectionDivider 
                            title="Busca Semântica" 
                            count={semanticResults.length}
                            icon="🧠"
                          />
                          <div className="space-y-4">
                            {semanticResults.map((result) => (
                              <SemanticSearchResultComponent
                                key={result.documento.id}
                                result={result}
                                searchTerm={searchTerm}
                                onClick={() => handleSemanticResultClick(result)}
                              />
                            ))}
                          </div>
                        </>
                      )}
                    </div>
                  ) : (
                    <NoResults searchTerm={searchTerm} />
                  )
                ) : researchers.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {researchers.map((researcher) => (
                      <ResearcherCard
                        key={researcher.id}
                        id={researcher.id}
                        name={researcher.name}
                        title={researcher.title}
                        photo={researcher.photo}
                        onClick={handleResearcherClick}
                      />
                    ))}
                  </div>
                ) : (
                  <NoResults searchTerm={searchTerm} />
                )}

                {/* Paginação */}
                {((searchMode === "articles" && (results.length > 0 || semanticResults.length > 0)) ||
                  (searchMode === "researchers" && researchers.length > 0)) && (
                  <SearchPagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={setCurrentPage}
                  />
                )}
              </>
            )}
          </div>
        )}
      </main>

      {/* Overlay de artigo */}
      <ArticleOverlay
        article={selectedArticle}
        isOpen={isOverlayOpen}
        onClose={() => setIsOverlayOpen(false)}
        onAuthorClick={handleAuthorClick}
      />
    </div>
  );
};

export default Index;
