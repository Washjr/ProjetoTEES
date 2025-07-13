import { ArticleData } from "./article";

export interface ResearcherData {
  id: string;
  name: string;
  title: string;
  photo: string;
}

// export interface AcademicHistoryItem {
//   year: string;
//   title: string;
//   institution: string;
// }

export interface ResearcherProfileData {
  researcher: ResearcherData;
  productions: ArticleData[];
  resumo_ia: string;
  tags: string[];
  // academicHistory: AcademicHistoryItem[];
}