export interface ArticleData {
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