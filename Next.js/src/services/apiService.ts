import { ArticleData, ResearcherData, ResultArticleData, SemanticSearchData, CombinedSearchData } from '../types';
import { ResearcherProfileData, ResumeData } from '../types/researcher';
// Para testes sem backend, descomente a linha abaixo e comente as funções do ApiService
// import { ApiServiceTest as ApiService } from './apiServiceTest';

// Constante para facilitar a troca quando a API estiver pronta
const API_BASE_URL = "http://127.0.0.1:8000";

export class ApiService {
  /**
   * Busca artigos baseado no termo de pesquisa
   * Para usar dados mockados para teste, comente este método e descomente o import do ApiServiceTest
   */
  static async searchArticles(searchTerm: string, incluirResumo: boolean = true): Promise<ResultArticleData> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/artigos/buscar?termo=${encodeURIComponent(searchTerm)}&incluir_resumo=${incluirResumo}`
      );
      
      if (!response.ok) {
        throw new Error(`Erro ao buscar artigos: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Dados recebidos do backend:', data);
      
      // Verificar se a resposta já está no formato correto
      if (data.resultados && typeof data.resumo_ia !== 'undefined') {
        console.log('Resposta já no formato correto:', data);
        // Garantir que tags existe, mesmo que vazio
        return {
          ...data,
          tags: data.tags || []
        };
      }
      
      // Se não estiver no formato correto, transformar
      const articles: ArticleData[] = Array.isArray(data) ? data : data.resultados || [];
      
      // Transformar o resultado para o formato esperado pelo frontend
      const result: ResultArticleData = {
        resultados: articles,
        resumo_ia: incluirResumo ? (data.resumo_ia || "Resumo gerado pela IA baseado nos resultados da busca.") : "",
        tags: data.tags || []
      };
      
      console.log('Resultado transformado:', result);
      return result;
    } catch (error) {
      console.error('Erro ao buscar artigos:', error);
      throw error;
    }
  }

  /**
   * Busca semântica de artigos baseado no termo de pesquisa
   */
  static async searchArticlesSemantic(searchTerm: string): Promise<SemanticSearchData> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/artigos/busca_semantica?termo=${encodeURIComponent(searchTerm)}&k=10`
      );
      
      if (!response.ok) {
        throw new Error(`Erro na busca semântica: ${response.status} ${response.statusText}`);
      }
      
      const data: SemanticSearchData = await response.json();
      console.log('Dados da busca semântica:', data);
      return data;
    } catch (error) {
      console.error('Erro na busca semântica:', error);
      throw error;
    }
  }

  /**
   * Busca combinada: termo + semântica
   */
  static async searchArticlesCombined(searchTerm: string, incluirResumo: boolean = true): Promise<CombinedSearchData> {
    try {
      // Executar ambas as buscas em paralelo
      const [termoBusca, buscaSemantica] = await Promise.all([
        this.searchArticles(searchTerm, incluirResumo),
        this.searchArticlesSemantic(searchTerm)
      ]);

      return {
        termo_busca: termoBusca,
        busca_semantica: buscaSemantica
      };
    } catch (error) {
      console.error('Erro na busca combinada:', error);
      throw error;
    }
  }

  /**
   * Busca pesquisadores baseado no termo de pesquisa
   * Para usar dados mockados para teste, comente este método e descomente o import do ApiServiceTest
   */
  static async searchResearchers(searchTerm: string): Promise<ResearcherData[]> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/pesquisadores/buscar?termo=${encodeURIComponent(searchTerm)}`
      );
      
      if (!response.ok) {
        throw new Error(`Erro ao buscar pesquisadores: ${response.status} ${response.statusText}`);
      }
      
      const researchers: ResearcherData[] = await response.json();
      return researchers;
    } catch (error) {
      console.error('Erro ao buscar pesquisadores:', error);
      throw error;
    }
  }

  /**
   * Busca detalhes de um pesquisador pelo ID
   * Para usar dados mockados para teste, comente este método e descomente o import do ApiServiceTest
   */
  static async getResearcherById(id: string): Promise<ResearcherData | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/pesquisadores/${id}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          return null;
        }
        throw new Error(`Erro ao buscar pesquisador: ${response.status} ${response.statusText}`);
      }
      
      const researcher: ResearcherData = await response.json();
      return researcher;
    } catch (error) {
      console.error('Erro ao buscar pesquisador:', error);
      throw error;
    }
  }

  /**
   * Busca detalhes de um artigo pelo ID
   * Para usar dados mockados para teste, comente este método e descomente o import do ApiServiceTest
   */
  static async getArticleById(id: string): Promise<ArticleData | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/artigos/${id}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          return null;
        }
        throw new Error(`Erro ao buscar artigo: ${response.status} ${response.statusText}`);
      }
      
      const article: ArticleData = await response.json();
      return article;
    } catch (error) {
      console.error('Erro ao buscar artigo:', error);
      throw error;
    }
  }

  /**
   * Busca perfil completo de um pesquisador pelo ID
   * Para usar dados mockados para teste, comente este método e descomente o import do ApiServiceTest
   */
  static async getResearcherProfile(id: string): Promise<ResearcherProfileData | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/pesquisadores/${id}/perfil`);
      
      if (!response.ok) {
        if (response.status === 404) {
          return null;
        }
        throw new Error(`Erro ao buscar perfil do pesquisador: ${response.status} ${response.statusText}`);
      }
      
      const profile: ResearcherProfileData = await response.json();
      return profile;
    } catch (error) {
      console.error('Erro ao buscar perfil do pesquisador:', error);
      throw error;
    }
  }

  /**
   * Busca resumo e tags de um pesquisador pelo ID
   * Para usar dados mockados para teste, comente este método e descomente o import do ApiServiceTest
   */
  static async getResearcherSummary(id: string): Promise<ResumeData | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/pesquisadores/${id}/resumo`);
      
      if (!response.ok) {
        if (response.status === 404) {
          return null;
        }
        throw new Error(`Erro ao buscar resumo do pesquisador: ${response.status} ${response.statusText}`);
      }
      
      const summary: ResumeData = await response.json();
      return summary;
    } catch (error) {
      console.error('Erro ao buscar resumo do pesquisador:', error);
      throw error;
    }
  }
}

/*
 * INSTRUÇÕES PARA ALTERNAR ENTRE MODO PRODUÇÃO E TESTE:
 * 
 * MODO PRODUÇÃO (atual - conecta ao backend real):
 * - Mantém o código como está
 * - Usa as funções do ApiService que fazem chamadas HTTP reais
 * 
 * MODO TESTE (usa dados mockados):
 * 1. Descomente a linha: import { ApiServiceTest as ApiService } from './apiServiceTest';
 * 2. Comente a linha: import { ArticleData, ResearcherData, ResultArticleData } from '../types';
 * 3. Comente toda a classe ApiService (linhas 8-85)
 * 
 * Dessa forma, o import renomeado fará com que o ApiServiceTest seja usado
 * no lugar do ApiService em todo o projeto, sem precisar alterar outras partes do código.
 */
