import React from "react";
import SearchInterface from "@/components/SearchInterface";
import SearchResult from "@/components/SearchResult";
import SearchSectionDivider from "@/components/SearchSectionDivider";
import LoadingSpinner from "@/components/LoadingSpinner";
import NoResults from "@/components/NoResults";
import ArticleOverlay from "@/components/ArticleOverlay";
import SearchPagination from "@/components/SearchPagination";
import FilterDisplay from "@/components/FilterDisplay";
import { useSearch, useArticleOverlay, usePagination } from "@/hooks";
import { useLayout } from "@/contexts/LayoutContext";

const Index = () => {
  const { setLayoutConfig } = useLayout();
  // Custom hooks para gerenciar estados e lógica
  const search = useSearch();
  const articleOverlay = useArticleOverlay();
  const pagination = usePagination({
    totalResults: search.getTotalResults(),
    itemsPerPage: 10
  });

  // Configurar o layout para ocultar o botão de volta
  React.useEffect(() => {
    setLayoutConfig({
      showBackButton: false
    });
  }, [setLayoutConfig]);

  // Reset pagination when search changes
  React.useEffect(() => {
    pagination.resetPagination();
  }, [search.searchTerm]);

  return (
    <>
      {/* Seção de busca centralizada */}
      <div
        className={`transition-all duration-500 ${
          search.hasSearched
            ? "mb-8 flex justify-center"
            : "min-h-[60vh] flex items-center justify-center"
        }`}
      >
          <div className={`w-full ${search.hasSearched ? "max-w-2xl" : "max-w-4xl"}`}>
            {!search.hasSearched && (
              <div className="max-w-4xl mx-auto text-center mb-12">
                <h1 className="text-5xl font-bold text-slate-800 mb-4 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  Pesquisa Acadêmica
                </h1>
                <p className="text-xl text-slate-600 mb-2">
                  Descubra pesquisas inovadoras da Universidade do Estado da Bahia
                </p>
                <p className="text-lg text-slate-500">
                  Pesquise artigos científicos publicados pelos professores
                </p>
              </div>
            )}

            <SearchInterface onSearch={search.handleSearch} isLoading={search.isLoading} />

            {!search.hasSearched && (
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
                      🧠
                    </span>
                  </div>
                  <h3 className="font-semibold text-slate-800 mb-2">
                    Busca Semântica
                  </h3>
                  <p className="text-sm text-slate-600">
                    Busca inteligente que compreende o contexto da pesquisa
                  </p>
                </div>

                <div className="text-center p-6 bg-white/70 backdrop-blur-sm rounded-xl border border-slate-200/50 shadow-sm hover:shadow-md transition-shadow relative z-0">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg mx-auto mb-4 flex items-center justify-center">
                    <span className="text-purple-600 text-xl font-semibold">
                      �
                    </span>
                  </div>
                  <h3 className="font-semibold text-slate-800 mb-2">
                    Busca Avançada
                  </h3>
                  <p className="text-sm text-slate-600">
                    Filtre por ano, Qualis e outras características específicas
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Resultados da busca */}
        {search.hasSearched && (
          <div className="max-w-6xl mx-auto">
            {search.isLoading ? (
              <LoadingSpinner />
            ) : (
              <>
                {/* Filtros usados na busca */}
                {(search.contentQuery || search.filterInterface) && (
                  <FilterDisplay
                    contentQuery={search.contentQuery || search.searchTerm}
                    filterInterface={search.filterInterface}
                  />
                )}

                {/* Resultados */}
                {(search.results.length > 0 || search.semanticResults.length > 0) ? (
                    <div className="space-y-6">
                      {/* Resultados por termo */}
                      {search.results.length > 0 && (
                        <>
                          <SearchSectionDivider 
                            title="Busca por Termo" 
                            count={search.results.length}
                            icon="🔤"
                          />
                          <div className="space-y-4">
                            {search.results.map((result) => (
                              <SearchResult
                                key={result.id}
                                title={result.title}
                                journal={result.journal}
                                year={result.year}
                                qualis={result.qualis}
                                abstract={result.abstract}
                                authors={Array.isArray(result.authors) ? (typeof result.authors[0] === 'string' ? result.authors : result.authors.map(a => a.name)) : []}
                                searchTerm={search.searchTerm}
                                onClick={() => articleOverlay.handleArticleClick(result)}
                              />
                            ))}
                          </div>
                        </>
                      )}

                      {/* Resultados semânticos */}
                      {search.semanticResults.length > 0 && (
                        <>
                          <SearchSectionDivider 
                            title="Busca Semântica" 
                            count={search.semanticResults.length}
                            icon="🧠"
                          />
                          <div className="space-y-4">
                            {search.semanticResults.map((result) => (
                              <SearchResult
                                key={result.documento?.id || result.id}
                                isSemanticSearch={true}
                                semanticResult={result}
                                searchTerm={search.searchTerm}
                                onClick={() => articleOverlay.handleSemanticResultClick(result)}
                              />
                            ))}
                          </div>
                        </>
                      )}
                    </div>
                  ) : (
                    <NoResults searchTerm={search.searchTerm} />
                  )
                }

                {/* Paginação */}
                {search.hasResults() && (
                  <SearchPagination
                    currentPage={pagination.currentPage}
                    totalPages={pagination.totalPages}
                    onPageChange={pagination.setCurrentPage}
                  />
                )}
              </>
            )}
          </div>
        )}

      {/* Overlay de artigo */}
      <ArticleOverlay
        article={articleOverlay.selectedArticle}
        isOpen={articleOverlay.isOverlayOpen}
        onClose={articleOverlay.closeOverlay}
        onAuthorClick={articleOverlay.handleAuthorClick}
      />
    </>
  );
};

export default Index;
