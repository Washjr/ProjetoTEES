export interface ArticleData {
  id: string;
  title: string;
  journal: string;
  year: number;
  issue?: string;
  abstract: string;
  doi?: string;
  authors: Array<{ id: string; name: string }>;
  qualis?: 'A1' | 'A2' | 'A3' | 'A4' | 'B1' | 'B2' | 'B3' | 'B4' | 'C' | 'NP';
}