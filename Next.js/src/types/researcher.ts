import { ArticleData } from "./article";

export interface ResearcherData {
  id: string;
  name: string;
  title: string;
  photo: string;
}

export interface ResearcherProfileData {
  researcher: ResearcherData;
  productions: ArticleData[];
}

export interface ResumeData {
  resumo_ia: string;
  tags: string[];
}