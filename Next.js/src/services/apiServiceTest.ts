import { ArticleData, ResearcherData, ResultArticleData } from '../types';
import { ResearcherProfileData } from '../types/researcher';
// import { AcademicHistoryItem } from '../types/researcher';

// Dados de exemplo baseados no formato real da API
const mockArticles: ArticleData[] = [
  {
    id: "0c9ea3bf-7892-4959-af55-a301ea663478",
    title: "A Framework For Context-Aware Systems In Mobile Devices",
    journal: "Lecture Notes In Computer Science",
    year: 2012,
    abstract: "",
    doi: null,
    qualis: "SQ",
    authors: [
      {
        id: "faec706b-c321-4bea-8026-fc20ced12885",
        name: "Eduardo Manuel de Freitas Jorge"
      }
    ]
  },
  {
    id: "94f881fe-b00c-474e-9d4b-d5015cfa8873",
    title: "A Mobile, Lightweight, Poll-Based Food Identification System",
    journal: "Pattern Recognition",
    year: 2014,
    abstract: "",
    doi: "10.1016/j.patcog.2013.12.006",
    qualis: "A1",
    authors: [
      {
        id: "faec706b-c321-4bea-8026-fc20ced12885",
        name: "Eduardo Manuel de Freitas Jorge"
      }
    ]
  },
  {
    id: "b66863cd-18aa-4377-a324-9b586c2d2852",
    title: "Protótipo De Aplicativo Móvel: Proposta Para Apoio Ao Turismo Acessível No Pelourinho Em Salvador (ba) No Contexto Da Pessoa Idosa",
    journal: "International Journal Of Scientific Management And Tourism",
    year: 2024,
    abstract: "O objetivo deste artigo foi criar uma solução tecnológica, estruturando um protótipo de aplicativo mobile para apoiar o turismo no contexto da pessoa idosa. A proposta surgiu devido à falta de informações adequadas sobre turismo acessível no Pelourinho. A metodologia adotada utilizou uma abordagem qualitativa de caráter exploratório, influenciada por algumas técnicas do design thinking. Os resultados da pesquisa mostram os requisitos funcionais, estruturados com base nas principais características, padrões e critérios do público-alvo. Foram elaborados alguns esboços para atender aos requisitos estabelecidos, utilizando wireframes de baixa fidelidade e a ferramenta de design FIGMA. Além disso, foi realizada a materialização da interface do aplicativo. Este artigo apresenta um protótipo para localização e avaliação de locais acessíveis ao público-alvo no Pelourinho, um local turístico e de lazer em Salvador, Bahia. A prototipagem pode servir como referência para estudos futuros, ao apresentar os principais requisitos funcionais dos aplicativos utilizados para apoiar o turismo acessível no país, podendo ser expandida para outros locais ou até mesmo para outras cidades.",
    doi: "10.55905/ijsmtv10n4-030",
    qualis: "A4",
    authors: [
      {
        id: "faec706b-c321-4bea-8026-fc20ced12885",
        name: "Eduardo Manuel de Freitas Jorge"
      }
    ]
  },
  {
    id: "a1b2c3d4-5678-9012-3456-789012345678",
    title: "Machine Learning Applications in Healthcare Diagnostics",
    journal: "Nature Medicine",
    year: 2023,
    abstract: "Recent developments in machine learning have revolutionized healthcare diagnostics, enabling more accurate and faster detection of diseases. This study presents a comprehensive analysis of machine learning algorithms applied to medical imaging and patient data, demonstrating significant improvements in diagnostic accuracy across multiple medical specialties.",
    doi: "10.1038/s41591-023-01234-5",
    qualis: "A1",
    authors: [
      {
        id: "researcher-001",
        name: "Dr. Maria Silva Santos"
      },
      {
        id: "researcher-002",
        name: "Dr. João Paulo Lima"
      }
    ]
  },
  {
    id: "e5f6g7h8-9012-3456-7890-123456789012",
    title: "Climate Change Impact on Marine Ecosystems",
    journal: "Environmental Science",
    year: 2023,
    abstract: "This comprehensive study examines the effects of climate change on marine biodiversity and ecosystem stability. Through extensive data analysis and field research, we demonstrate significant correlations between rising ocean temperatures and species migration patterns.",
    doi: "10.1016/j.envres.2023.01234",
    qualis: "A1",
    authors: [
      {
        id: "researcher-003",
        name: "Dra. Ana Costa Ferreira"
      },
      {
        id: "researcher-004",
        name: "Dr. Carlos Eduardo Silva"
      }
    ]
  }
];

const mockResearchers: ResearcherData[] = [
  {
    id: "faec706b-c321-4bea-8026-fc20ced12885",
    name: "Eduardo Manuel de Freitas Jorge",
    title: "Doutor em Ciência da Computação",
    photo: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face",
  },
  {
    id: "researcher-001",
    name: "Dr. Maria Silva Santos",
    title: "Doutora em Ciência da Computação",
    photo: "https://images.unsplash.com/photo-1494790108755-2616b612b5bc?w=400&h=400&fit=crop&crop=face",
  },
  {
    id: "researcher-002",
    name: "Dr. João Paulo Lima",
    title: "Doutor em Inteligência Artificial",
    photo: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face",
  },
  {
    id: "researcher-003",
    name: "Dra. Ana Costa Ferreira",
    title: "Doutora em Medicina",
    photo: "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=400&h=400&fit=crop&crop=face",
  },
  {
    id: "researcher-004",
    name: "Dr. Carlos Eduardo Silva",
    title: "Doutor em Engenharia Biomédica",
    photo: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face",
  },
];

// Dados mockados para perfis completos dos pesquisadores
const mockResearcherProfiles: { [key: string]: ResearcherProfileData } = {
  "researcher-001": {
    researcher: {
      id: "researcher-001",
      name: "Dr. Maria Silva Santos",
      title: "Doutora em Ciência da Computação",
      photo: "https://images.unsplash.com/photo-1494790108755-2616b612b5bc?w=400&h=400&fit=crop&crop=face",
    },
    resumo_ia: "Dr. Maria Silva Santos é uma pesquisadora renomada na área de Ciência da Computação, com foco em aplicações de inteligência artificial em diagnósticos médicos. Seus trabalhos têm contribuído significativamente para avanços na precisão diagnóstica e na eficiência dos sistemas de saúde.",
    tags: ["Inteligência Artificial", "Saúde", "Diagnóstico Médico"],
    productions: [
      {
        id: "1",
        title: "Machine Learning Applications in Healthcare: A Comprehensive Review",
        journal: "Nature Medicine",
        year: 2023,
        abstract: "This comprehensive review examines the latest machine learning applications in healthcare, focusing on diagnostic accuracy and patient outcomes...",
        doi: "10.1038/s41591-023-01234-5",
        qualis: "A1",
        authors: [
          {
            id: "researcher-001",
            name: "Dr. Maria Silva Santos"
          }
        ]
      },
      {
        id: "2",
        title: "Deep Learning for Medical Image Analysis",
        journal: "IEEE Transactions on Medical Imaging",
        year: 2022,
        abstract: "We present a novel deep learning approach for medical image analysis that achieves state-of-the-art results in tumor detection...",
        doi: "10.1109/TMI.2022.01234",
        qualis: "A2",
        authors: [
          {
            id: "researcher-001",
            name: "Dr. Maria Silva Santos"
          }
        ]
      }
    ]
    // academicHistory: [
    //   { year: "2020", title: "Doutorado em Ciência da Computação", institution: "Universidade de São Paulo" },
    //   { year: "2016", title: "Mestrado em Inteligência Artificial", institution: "UNICAMP" },
    //   { year: "2014", title: "Bacharelado em Ciência da Computação", institution: "UFRJ" }
    // ]
  },
  "faec706b-c321-4bea-8026-fc20ced12885": {
    researcher: {
      id: "faec706b-c321-4bea-8026-fc20ced12885",
      name: "Eduardo Manuel de Freitas Jorge",
      title: "Doutor em Ciência da Computação",
      photo: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face",
    },
    resumo_ia: "Eduardo Manuel de Freitas Jorge é um pesquisador ativo na área de Ciência da Computação, com ênfase em sistemas móveis e acessibilidade. Seus estudos visam melhorar a experiência do usuário em dispositivos móveis, especialmente para populações vulneráveis.",
    tags: ["Sistemas Móveis", "Acessibilidade", "Tecnologia Assistiva"],
    productions: [
      {
        id: "0c9ea3bf-7892-4959-af55-a301ea663478",
        title: "A Framework For Context-Aware Systems In Mobile Devices",
        journal: "Lecture Notes In Computer Science",
        year: 2012,
        abstract: "",
        doi: null,
        qualis: "SQ",
        authors: [
          {
            id: "faec706b-c321-4bea-8026-fc20ced12885",
            name: "Eduardo Manuel de Freitas Jorge"
          }
        ]
      },
      {
        id: "94f881fe-b00c-474e-9d4b-d5015cfa8873",
        title: "A Mobile, Lightweight, Poll-Based Food Identification System",
        journal: "Pattern Recognition",
        year: 2014,
        abstract: "",
        doi: "10.1016/j.patcog.2013.12.006",
        qualis: "A1",
        authors: [
          {
            id: "faec706b-c321-4bea-8026-fc20ced12885",
            name: "Eduardo Manuel de Freitas Jorge"
          }
        ]
      },
      {
        id: "b66863cd-18aa-4377-a324-9b586c2d2852",
        title: "Protótipo De Aplicativo Móvel: Proposta Para Apoio Ao Turismo Acessível No Pelourinho Em Salvador (ba) No Contexto Da Pessoa Idosa",
        journal: "International Journal Of Scientific Management And Tourism",
        year: 2024,
        abstract: "O objetivo deste artigo foi criar uma solução tecnológica, estruturando um protótipo de aplicativo mobile para apoiar o turismo no contexto da pessoa idosa. A proposta surgiu devido à falta de informações adequadas sobre turismo acessível no Pelourinho. A metodologia adotada utilizou uma abordagem qualitativa de caráter exploratório, influenciada por algumas técnicas do design thinking. Os resultados da pesquisa mostram os requisitos funcionais, estruturados com base nas principais características, padrões e critérios do público-alvo. Foram elaborados alguns esboços para atender aos requisitos estabelecidos, utilizando wireframes de baixa fidelidade e a ferramenta de design FIGMA. Além disso, foi realizada a materialização da interface do aplicativo. Este artigo apresenta um protótipo para localização e avaliação de locais acessíveis ao público-alvo no Pelourinho, um local turístico e de lazer em Salvador, Bahia. A prototipagem pode servir como referência para estudos futuros, ao apresentar os principais requisitos funcionais dos aplicativos utilizados para apoiar o turismo acessível no país, podendo ser expandida para outros locais ou até mesmo para outras cidades.",
        doi: "10.55905/ijsmtv10n4-030",
        qualis: "A4",
        authors: [
          {
            id: "faec706b-c321-4bea-8026-fc20ced12885",
            name: "Eduardo Manuel de Freitas Jorge"
          }
        ]
      }
    ]
    // academicHistory: [
    //   { year: "2018", title: "Doutorado em Ciência da Computação", institution: "Universidade Federal da Bahia" },
    //   { year: "2014", title: "Mestrado em Sistemas e Computação", institution: "UFBA" },
    //   { year: "2012", title: "Bacharelado em Ciência da Computação", institution: "UFBA" }
    // ]
  }
};

/**
 * Serviço de API para testes - usa dados mockados
 * Use este serviço quando quiser testar sem conectar ao backend
 */
export class ApiServiceTest {
  /**
   * Busca artigos baseado no termo de pesquisa (versão de teste)
   */
  static async searchArticles(searchTerm: string, incluirResumo: boolean = false): Promise<ResultArticleData> {
    try {
      // Simular delay da API
      await new Promise((resolve) => setTimeout(resolve, 1500));
      
      // Filtrar artigos baseado no termo de busca
      const filteredArticles = mockArticles.filter(article => 
        article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        article.abstract.toLowerCase().includes(searchTerm.toLowerCase()) ||
        article.journal.toLowerCase().includes(searchTerm.toLowerCase()) ||
        article.authors.some(author => author.name.toLowerCase().includes(searchTerm.toLowerCase()))
      );
      
      // Gerar resumo da IA se solicitado
      const resumoIA = incluirResumo 
        ? `Esta busca por "${searchTerm}" retornou ${filteredArticles.length} artigo(s) relevante(s). Os resultados abrangem diferentes áreas de pesquisa e demonstram a diversidade de trabalhos relacionados ao termo buscado.`
        : "";
      
      const result: ResultArticleData = {
        resultados: filteredArticles,
        resumo_ia: resumoIA
      };
      
      return result;
    } catch (error) {
      console.error('Erro ao buscar artigos (teste):', error);
      throw error;
    }
  }

  /**
   * Busca pesquisadores baseado no termo de pesquisa (versão de teste)
   */
  static async searchResearchers(searchTerm: string): Promise<ResearcherData[]> {
    try {
      // Simular delay da API
      await new Promise((resolve) => setTimeout(resolve, 1500));
      
      // Filtrar pesquisadores baseado no termo de busca
      const filteredResearchers = mockResearchers.filter(researcher =>
        researcher.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        researcher.title.toLowerCase().includes(searchTerm.toLowerCase())
      );
      
      return filteredResearchers;
    } catch (error) {
      console.error('Erro ao buscar pesquisadores (teste):', error);
      throw error;
    }
  }

  /**
   * Busca detalhes de um pesquisador pelo ID (versão de teste)
   */
  static async getResearcherById(id: string): Promise<ResearcherData | null> {
    try {
      // Simular delay da API
      await new Promise((resolve) => setTimeout(resolve, 800));
      
      const researcher = mockResearchers.find(researcher => researcher.id === id);
      return researcher || null;
    } catch (error) {
      console.error('Erro ao buscar pesquisador (teste):', error);
      throw error;
    }
  }

  /**
   * Busca detalhes de um artigo pelo ID (versão de teste)
   */
  static async getArticleById(id: string): Promise<ArticleData | null> {
    try {
      // Simular delay da API
      await new Promise((resolve) => setTimeout(resolve, 800));
      
      const article = mockArticles.find(article => article.id === id);
      return article || null;
    } catch (error) {
      console.error('Erro ao buscar artigo (teste):', error);
      throw error;
    }
  }

  /**
   * Busca perfil completo de um pesquisador pelo ID (versão de teste)
   */
  static async getResearcherProfile(id: string): Promise<ResearcherProfileData | null> {
    try {
      // Simular delay da API
      await new Promise((resolve) => setTimeout(resolve, 1200));
      
      const profile = mockResearcherProfiles[id];
      return profile || null;
    } catch (error) {
      console.error('Erro ao buscar perfil do pesquisador (teste):', error);
      throw error;
    }
  }

  /**
   * Retorna todos os artigos mockados (útil para testes)
   */
  static getAllMockArticles(): ArticleData[] {
    return mockArticles;
  }

  /**
   * Retorna todos os pesquisadores mockados (útil para testes)
   */
  static getAllMockResearchers(): ResearcherData[] {
    return mockResearchers;
  }

  /**
   * Retorna todos os perfis completos mockados (útil para testes)
   */
  static getAllMockResearcherProfiles(): { [key: string]: ResearcherProfileData } {
    return mockResearcherProfiles;
  }
}
