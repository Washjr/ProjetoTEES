import { QualitsClassification } from '@/lib/utils';

export interface ArticleData {
  id: string;
  title: string;
  journal: string;
  year: number;
  abstract: string;
  doi?: string | null;
  authors: string[] | Array<{ id: string; name: string }>;
  qualis?: QualitsClassification;
  score?: number | null;
}

export interface SemanticSearchResult {
  documento?: ArticleData;
  score: number;
  // Permitir que os dados semânticos venham diretamente no resultado
  id?: string;
  title?: string;
  journal?: string;
  year?: number;
  abstract?: string;
  doi?: string | null;
  authors?: string[];
  qualis?: QualitsClassification;
}

export interface StructuredQuery {
  content_query: string;
  filter_interface: string;
  filter_selfquery: string;
}

export interface SearchStats {
  total_resultados: number;
}

export interface SearchResults {
  termos: ArticleData[];
  semanticos: SemanticSearchResult[];
}

// Nova interface para a resposta combinada da API
export interface NewApiResponse {
  query: string;
  structured_query: StructuredQuery;
  search_stats: SearchStats;
  results: SearchResults;
}

export interface SemanticSearchData {
  query: string;
  resultados: SemanticSearchResult[];
}

export interface ResultArticleData {
  resultados: ArticleData[];
  resumo_ia: string;
  tags: string[];
}

export interface CombinedSearchData {
  termo_busca: ResultArticleData;
  busca_semantica: SemanticSearchData;
}