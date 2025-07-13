import { ArticleData, ResearcherData, ResultArticleData } from '../types';

// Constante para facilitar a troca quando a API estiver pronta
const API_BASE_URL = "http://127.0.0.1:8000";

// Dados de exemplo (serão removidos quando a API estiver pronta)
const mockResult: ResultArticleData = {
  resultados: [
    {
      id: "1",
      title:
        "Advances in Machine Learning Applications for Healthcare Diagnostics",
      journal: "Nature Medicine",
      year: 2023,
      issue: "3",
      abstract:
        "Recent developments in machine learning have revolutionized healthcare diagnostics, enabling more accurate and faster detection of diseases. This study presents a comprehensive analysis of machine learning algorithms applied to medical imaging and patient data, demonstrating significant improvements in diagnostic accuracy across multiple medical specialties.",
      doi: "10.1038/s41591-023-01234-5",
      authors: [
        { id: "1", name: "Dr. Maria Silva Santos" },
        { id: "2", name: "Dr. João Paulo Lima" },
      ],
      qualis: "A1",
    },
    {
      id: "2",
      title: "Climate Change Impact on Marine Ecosystems",
      journal: "Environmental Science",
      year: 2023,
      issue: "2",
      qualis: "A1",
      abstract:
        "This comprehensive study examines the effects of climate change on marine biodiversity and ecosystem stability. Through extensive data analysis and field research, we demonstrate significant correlations between rising ocean temperatures and species migration patterns.",
      doi: "10.1016/j.envres.2023.01234",
      authors: [
        { id: "3", name: "Dra. Ana Costa Ferreira" },
        { id: "4", name: "Dr. Carlos Eduardo Silva" },
      ],
    },
  ],
  resumo_ia: "Esta busca retornou artigos relevantes sobre machine learning em healthcare e mudanças climáticas em ecossistemas marinhos. Ambos os estudos demonstram avanços significativos em suas respectivas áreas, com metodologias robustas e resultados impactantes para a comunidade científica.",
};

const mockResearchers: ResearcherData[] = [
  {
    id: "1",
    name: "Dr. Maria Silva Santos",
    title: "Doutora em Ciência da Computação",
    photo:
      "https://images.unsplash.com/photo-1494790108755-2616b612b5bc?w=400&h=400&fit=crop&crop=face",
  },
  {
    id: "2",
    name: "Dr. João Paulo Lima",
    title: "Doutor em Inteligência Artificial",
    photo:
      "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face",
  },
  {
    id: "3",
    name: "Dra. Ana Costa Ferreira",
    title: "Doutora em Medicina",
    photo:
      "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=400&h=400&fit=crop&crop=face",
  },
  {
    id: "4",
    name: "Dr. Carlos Eduardo Silva",
    title: "Doutor em Engenharia Biomédica",
    photo:
      "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face",
  },
];

export class ApiService {
  /**
   * Busca artigos baseado no termo de pesquisa
   */
  static async searchArticles(searchTerm: string): Promise<ResultArticleData> {
    try {
      // TODO: Implementar chamada real da API quando estiver pronta
      // const response = await fetch(`${API_BASE_URL}/articles/search?q=${encodeURIComponent(searchTerm)}`);
      // if (!response.ok) {
      //   throw new Error('Erro ao buscar artigos');
      // }
      // return await response.json();

      // Simular delay da API
      await new Promise((resolve) => setTimeout(resolve, 2000));
      
      // Retorno temporário com dados de exemplo (a API já retornará os resultados filtrados)
      return mockResult;
    } catch (error) {
      console.error('Erro ao buscar artigos:', error);
      throw error;
    }
  }

  /**
   * Busca pesquisadores baseado no termo de pesquisa
   */
  static async searchResearchers(searchTerm: string): Promise<ResearcherData[]> {
    try {
      // TODO: Implementar chamada real da API quando estiver pronta
      // const response = await fetch(`${API_BASE_URL}/researchers/search?q=${encodeURIComponent(searchTerm)}`);
      // if (!response.ok) {
      //   throw new Error('Erro ao buscar pesquisadores');
      // }
      // return await response.json();

      // Simular delay da API
      await new Promise((resolve) => setTimeout(resolve, 2000));
      
      // Retorno temporário com dados de exemplo (a API já retornará os resultados filtrados)
      return mockResearchers;
    } catch (error) {
      console.error('Erro ao buscar pesquisadores:', error);
      throw error;
    }
  }

  /**
   * Busca detalhes de um pesquisador pelo ID
   */
  static async getResearcherById(id: string): Promise<ResearcherData | null> {
    try {
      // TODO: Implementar chamada real da API quando estiver pronta
      // const response = await fetch(`${API_BASE_URL}/researchers/${id}`);
      // if (!response.ok) {
      //   throw new Error('Pesquisador não encontrado');
      // }
      // return await response.json();

      // Simular delay da API
      await new Promise((resolve) => setTimeout(resolve, 1000));
      
      // Retorno temporário com dados de exemplo
      return mockResearchers.find(researcher => researcher.id === id) || null;
    } catch (error) {
      console.error('Erro ao buscar pesquisador:', error);
      throw error;
    }
  }

  /**
   * Busca detalhes de um artigo pelo ID
   */
  static async getArticleById(id: string): Promise<ArticleData | null> {
    try {
      // TODO: Implementar chamada real da API quando estiver pronta
      // const response = await fetch(`${API_BASE_URL}/articles/${id}`);
      // if (!response.ok) {
      //   throw new Error('Artigo não encontrado');
      // }
      // return await response.json();

      // Simular delay da API
      await new Promise((resolve) => setTimeout(resolve, 1000));
      
      // Retorno temporário com dados de exemplo
      return mockResult.resultados.find(article => article.id === id) || null;
    } catch (error) {
      console.error('Erro ao buscar artigo:', error);
      throw error;
    }
  }
}
