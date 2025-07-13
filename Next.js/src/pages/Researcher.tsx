
import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import SearchSummary from '@/components/SearchSummary';
import SearchResult from '@/components/SearchResult';

const Researcher = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // Dados mockados do pesquisador
  const researcher = {
    id: id || '1',
    name: 'Dr. Maria Silva Santos',
    title: 'Doutora em Ciência da Computação',
    photo: 'https://images.unsplash.com/photo-1494790108755-2616b612b5bc?w=400&h=400&fit=crop&crop=face',
    productions: [
      {
        id: '1',
        title: 'Machine Learning Applications in Healthcare: A Comprehensive Review',
        journal: 'Nature Medicine',
        year: 2023,
        issue: '3',
        qualis: 'A1' as const,
        abstract: 'This comprehensive review examines the latest machine learning applications in healthcare, focusing on diagnostic accuracy and patient outcomes...'
      },
      {
        id: '2',
        title: 'Deep Learning for Medical Image Analysis',
        journal: 'IEEE Transactions on Medical Imaging',
        year: 2022,
        issue: '8',
        qualis: 'A2' as const,
        abstract: 'We present a novel deep learning approach for medical image analysis that achieves state-of-the-art results in tumor detection...'
      }
    ],
    academicHistory: [
      { year: '2020', title: 'Doutorado em Ciência da Computação', institution: 'Universidade de São Paulo' },
      { year: '2016', title: 'Mestrado em Inteligência Artificial', institution: 'UNICAMP' },
      { year: '2014', title: 'Bacharelado em Ciência da Computação', institution: 'UFRJ' }
    ]
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header igual ao da página principal */}
      <header className="border-b border-slate-200/50 bg-white/70 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div 
              className="flex items-center space-x-3 cursor-pointer hover:opacity-80 transition-opacity"
              onClick={() => navigate('/')}
            >
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">AE</span>
              </div>
              <span className="font-semibold text-slate-800">
                Pesquisa Acadêmica
              </span>
            </div>
            <Button
              variant="ghost"
              onClick={() => navigate('/')}
              className="gap-2 text-slate-600 hover:text-slate-800"
            >
              <ArrowLeft className="h-4 w-4" />
              Voltar para busca
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Informações do pesquisador */}
        <div className="flex flex-col md:flex-row gap-6 mb-8 bg-white/70 backdrop-blur-sm rounded-xl border border-slate-200/50 shadow-sm p-6">
          <div className="flex-shrink-0">
            <img 
              src={researcher.photo} 
              alt={researcher.name}
              className="w-48 h-48 object-cover rounded-lg shadow-md"
            />
          </div>
          <div className="flex-1">
            <h1 className="text-3xl font-bold mb-2 text-slate-800">{researcher.name}</h1>
            <p className="text-xl text-slate-600 mb-4">{researcher.title}</p>
          </div>
        </div>

        {/* Resumo de pesquisa */}
        <SearchSummary
          totalResults={researcher.productions.length}
          topKeyword="machine learning"
          searchTerm={researcher.name}
        />

        {/* Produções */}
        <Card className="mb-8 bg-white/70 backdrop-blur-sm border-slate-200/50 shadow-sm">
          <CardHeader>
            <CardTitle className="text-slate-800">Produções Científicas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {researcher.productions.map((article) => (
                <SearchResult
                  key={article.id}
                  title={article.title}
                  journal={article.journal}
                  year={article.year}
                  issue={article.issue}
                  qualis={article.qualis}
                  abstract={article.abstract}
                  searchTerm=""
                />
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Histórico Acadêmico */}
        <Card className="bg-white/70 backdrop-blur-sm border-slate-200/50 shadow-sm">
          <CardHeader>
            <CardTitle className="text-slate-800">Histórico Acadêmico</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {researcher.academicHistory.map((item, index) => (
                <div key={index} className="flex gap-4 p-4 border border-slate-200/50 rounded-lg bg-white/50">
                  <Badge variant="outline" className="border-blue-200 text-blue-700">{item.year}</Badge>
                  <div>
                    <h3 className="font-semibold text-slate-800">{item.title}</h3>
                    <p className="text-slate-600">{item.institution}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default Researcher;
