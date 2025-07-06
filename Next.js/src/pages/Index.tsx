import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import SearchHeader from "@/components/SearchHeader";
import SearchBar from "@/components/SearchBar";
import SearchSummary from "@/components/SearchSummary";
import SearchResult from "@/components/SearchResult";
import LoadingSpinner from "@/components/LoadingSpinner";
import NoResults from "@/components/NoResults";
import ResearcherCard from "@/components/ResearcherCard";
import ArticleOverlay from "@/components/ArticleOverlay";
import SearchPagination from "@/components/SearchPagination";
import { ApiService } from "@/services/apiService";
import { ArticleData, ResearcherData } from "@/types";

const Index = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const [searchType, setSearchType] = useState<"artigo" | "pesquisador">(
    "artigo"
  );
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [results, setResults] = useState<ArticleData[]>([]);
  const [researchers, setResearchers] = useState<ResearcherData[]>([]);
  const [selectedArticle, setSelectedArticle] =
    useState<ArticleData | null>(null);
  const [isOverlayOpen, setIsOverlayOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const handleSearch = async () => {
    if (!searchTerm.trim()) return;

    setIsLoading(true);
    setHasSearched(true);
    setCurrentPage(1);

    try {
      if (searchType === "artigo") {
        const searchResults = await ApiService.searchArticles(searchTerm);
        setResults(searchResults);
        setTotalPages(Math.ceil(searchResults.length / 5));
      } else {
        const searchResearchers = await ApiService.searchResearchers(searchTerm);
        setResearchers(searchResearchers);
        setTotalPages(Math.ceil(searchResearchers.length / 8));
      }
    } catch (error) {
      console.error("Erro na busca:", error);
      // Em caso de erro, limpar os resultados
      setResults([]);
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

  const handleAuthorClick = (authorId: string) => {
    setIsOverlayOpen(false);
    navigate(`/researcher/${authorId}`);
  };

  const handleResearcherClick = (researcherId: string) => {
    navigate(`/researcher/${researcherId}`);
  };

  const getTotalResults = () =>
    searchType === "artigo" ? results.length : researchers.length;
  const getTopKeyword = () => {
    if (searchTerm.toLowerCase().includes("machine")) return "algoritmos";
    if (searchTerm.toLowerCase().includes("climate")) return "temperatura";
    return "pesquisa";
  };

  return (
    <div className="min-h-screen bg-background">
      <SearchHeader />

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
            <SearchBar
              searchTerm={searchTerm}
              onSearchChange={setSearchTerm}
              onSearch={handleSearch}
              isLoading={isLoading}
              searchType={searchType}
              onSearchTypeChange={setSearchType}
            />
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
                {searchType === "artigo" && results.length > 0 && (
                  <SearchSummary
                    totalResults={getTotalResults()}
                    topKeyword={getTopKeyword()}
                    searchTerm={searchTerm}
                  />
                )}

                {/* Resultados */}
                {searchType === "artigo" ? (
                  results.length > 0 ? (
                    <div className="space-y-4">
                      {results.map((result) => (
                        <SearchResult
                          key={result.id}
                          title={result.title}
                          journal={result.journal}
                          year={result.year}
                          volume={result.volume}
                          issue={result.issue}
                          abstractHighlight={result.abstractHighlight}
                          searchTerm={searchTerm}
                          onClick={() => handleArticleClick(result)}
                        />
                      ))}
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
                        hIndex={researcher.hIndex}
                        photo={researcher.photo}
                        onClick={handleResearcherClick}
                      />
                    ))}
                  </div>
                ) : (
                  <NoResults searchTerm={searchTerm} />
                )}

                {/* Paginação */}
                {((searchType === "artigo" && results.length > 0) ||
                  (searchType === "pesquisador" && researchers.length > 0)) && (
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
