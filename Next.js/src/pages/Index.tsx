import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "@/components/Layout";
import SearchInterface, { SearchMode } from "@/components/SearchInterface";
import SearchResult from "@/components/SearchResult";
import SearchSectionDivider from "@/components/SearchSectionDivider";
import LoadingSpinner from "@/components/LoadingSpinner";
import NoResults from "@/components/NoResults";
import ResearcherCard from "@/components/ResearcherCard";
import ArticleOverlay from "@/components/ArticleOverlay";
import SearchPagination from "@/components/SearchPagination";
import FilterDisplay from "@/components/FilterDisplay";
import { ApiService } from "@/services/apiService";
import { ArticleData, ResearcherData, SemanticSearchResult } from "@/types";

const Index = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [searchMode, setSearchMode] = useState<SearchMode>("articles");
  const [results, setResults] = useState<ArticleData[]>([]);
  const [semanticResults, setSemanticResults] = useState<SemanticSearchResult[]>([]);
  const [researchers, setResearchers] = useState<ResearcherData[]>([]);
  const [selectedArticle, setSelectedArticle] =
    useState<ArticleData | null>(null);
  const [isOverlayOpen, setIsOverlayOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filterInterface, setFilterInterface] = useState<string>("");
  const [contentQuery, setContentQuery] = useState<string>("");

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
        setTotalPages(Math.ceil(searchResearchers.length / 8));
      }
    } catch (error) {
      console.error("Erro na busca:", error);
      // Em caso de erro, limpar os resultados
      setResults([]);
      setSemanticResults([]);
      setResearchers([]);
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

  return (
    <>
      <Layout>
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
              <div className="mt-16 grid md:grid-cols-3 gap-8 max-w-3xl mx-auto relative z-0">
                <div className="text-center p-6 bg-white/70 backdrop-blur-sm rounded-xl border border-slate-200/50 shadow-sm hover:shadow-md transition-shadow relative z-0">
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

                <div className="text-center p-6 bg-white/70 backdrop-blur-sm rounded-xl border border-slate-200/50 shadow-sm hover:shadow-md transition-shadow relative z-0">
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

                <div className="text-center p-6 bg-white/70 backdrop-blur-sm rounded-xl border border-slate-200/50 shadow-sm hover:shadow-md transition-shadow relative z-0">
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
                {/* Filtros usados na busca */}
                {searchMode === "articles" && (contentQuery || filterInterface) && (
                  <FilterDisplay
                    contentQuery={contentQuery || searchTerm}
                    filterInterface={filterInterface}
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
                                authors={Array.isArray(result.authors) ? (typeof result.authors[0] === 'string' ? result.authors : result.authors.map(a => a.name)) : []}
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
                              <SearchResult
                                key={result.documento?.id || result.id}
                                isSemanticSearch={true}
                                semanticResult={result}
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
      </Layout>

      {/* Overlay de artigo */}
      <ArticleOverlay
        article={selectedArticle}
        isOpen={isOverlayOpen}
        onClose={() => setIsOverlayOpen(false)}
        onAuthorClick={handleAuthorClick}
      />
    </>
  );
};

export default Index;
