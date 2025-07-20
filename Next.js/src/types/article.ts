export interface ArticleData {
  id: string;
  title: string;
  journal: string;
  year: number;
  abstract: string;
  doi?: string | null;
  authors: Array<{ id: string; name: string }>;
  qualis?: 'A1' | 'A2' | 'A3' | 'A4' | 'B1' | 'B2' | 'B3' | 'B4' | 'C' | 'SQ';
}

export interface SemanticSearchResult {
  documento: ArticleData;
  score: number;
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