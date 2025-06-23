
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import SearchHeader from '@/components/SearchHeader';
import SearchBar from '@/components/SearchBar';
import SearchSummary from '@/components/SearchSummary';
import SearchResult from '@/components/SearchResult';
import LoadingSpinner from '@/components/LoadingSpinner';
import NoResults from '@/components/NoResults';
import ResearcherCard from '@/components/ResearcherCard';
import ArticleOverlay from '@/components/ArticleOverlay';
import SearchPagination from '@/components/SearchPagination';

interface SearchResultData {
  id: string;
  title: string;
  journal: string;
  year: number;
  volume?: string;
  issue?: string;
  abstractHighlight: string;
  abstract: string;
  doi?: string;
  authors: Array<{ id: string; name: string }>;
  tags: string[];
}

interface ResearcherData {
  id: string;
  name: string;
  title: string;
  hIndex: number;
  photo: string;
}

const Index = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [searchType, setSearchType] = useState<'artigo' | 'pesquisador'>('artigo');
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [results, setResults] = useState<SearchResultData[]>([]);
  const [researchers, setResearchers] = useState<ResearcherData[]>([]);
  const [selectedArticle, setSelectedArticle] = useState<SearchResultData | null>(null);
  const [isOverlayOpen, setIsOverlayOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Dados de exemplo para demonstração
  const mockResults: SearchResultData[] = [
    {
      id: '1',
      title: 'Advances in Machine Learning Applications for Healthcare Diagnostics',
      journal: 'Nature Medicine',
      year: 2023,
      volume: '29',
      issue: '3',
      abstractHighlight: 'Recent developments in machine learning have revolutionized healthcare diagnostics, enabling more accurate and faster detection of diseases...',
      abstract: 'Recent developments in machine learning have revolutionized healthcare diagnostics, enabling more accurate and faster detection of diseases. This study presents a comprehensive analysis of machine learning algorithms applied to medical imaging and patient data, demonstrating significant improvements in diagnostic accuracy across multiple medical specialties.',
      doi: '10.1038/s41591-023-01234-5',
      authors: [
        { id: '1', name: 'Dr. Maria Silva Santos' },
        { id: '2', name: 'Dr. João Paulo Lima' }
      ],
      tags: ['machine learning', 'healthcare', 'diagnostics', 'medical imaging']
    },
    // ... outros resultados similares
  ];

  const mockResearchers: ResearcherData[] = [
    {
      id: '1',
      name: 'Dr. Maria Silva Santos',
      title: 'Doutora em Ciência da Computação',
      hIndex: 25,
      photo: 'https://images.unsplash.com/photo-1494790108755-2616b612b5bc?w=400&h=400&fit=crop&crop=face'
    },
    {
      id: '2',
      name: 'Dr. João Paulo Lima',
      title: 'Doutor em Inteligência Artificial',
      hIndex: 18,
      photo: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face'
    },
    {
      id: '3',
      name: 'Dra. Ana Costa Ferreira',
      title: 'Doutora em Medicina',
      hIndex: 32,
      photo: 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=400&h=400&fit=crop&crop=face'
    },
    {
      id: '4',
      name: 'Dr. Carlos Eduardo Silva',
      title: 'Doutor em Engenharia Biomédica',
      hIndex: 22,
      photo: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face'
    }
  ];

  const handleSearch = async () => {
    if (!searchTerm.trim()) return;

    setIsLoading(true);
    setHasSearched(true);
    setCurrentPage(1);
    
    // Simular chamada de API
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    if (searchType === 'artigo') {
      const filteredResults = mockResults;
      setResults(filteredResults);
      setTotalPages(Math.ceil(filteredResults.length / 5));
    } else {
      const filteredResearchers = mockResearchers;
      setResearchers(filteredResearchers);
      setTotalPages(Math.ceil(filteredResearchers.length / 8));
    }
    
    setIsLoading(false);
  };

  const handleArticleClick = (article: SearchResultData) => {
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

  const getTotalResults = () => searchType === 'artigo' ? results.length : researchers.length;
  const getTopKeyword = () => {
    if (searchTerm.toLowerCase().includes('machine')) return 'algoritmos';
    if (searchTerm.toLowerCase().includes('climate')) return 'temperatura';
    return 'pesquisa';
  };

  return (
    <div className="min-h-screen bg-background">
      <SearchHeader />
      
      <main className="container mx-auto px-4 py-8">
        {/* Seção de busca centralizada */}
        <div className={`transition-all duration-500 ${hasSearched ? 'mb-8' : 'min-h-[60vh] flex items-center justify-center'}`}>
          <div className="w-full max-w-4xl">
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
                {searchType === 'artigo' && results.length > 0 && (
                  <SearchSummary
                    totalResults={getTotalResults()}
                    topKeyword={getTopKeyword()}
                    searchTerm={searchTerm}
                  />
                )}

                {/* Resultados */}
                {searchType === 'artigo' ? (
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
                ) : (
                  researchers.length > 0 ? (
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
                  )
                )}

                {/* Paginação */}
                {((searchType === 'artigo' && results.length > 0) || 
                  (searchType === 'pesquisador' && researchers.length > 0)) && (
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
