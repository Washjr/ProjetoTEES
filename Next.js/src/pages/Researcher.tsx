
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
    hIndex: 25,
    photo: 'https://images.unsplash.com/photo-1494790108755-2616b612b5bc?w=400&h=400&fit=crop&crop=face',
    productions: [
      {
        id: '1',
        title: 'Machine Learning Applications in Healthcare: A Comprehensive Review',
        journal: 'Nature Medicine',
        year: 2023,
        volume: '29',
        issue: '3',
        abstractHighlight: 'This comprehensive review examines the latest machine learning applications in healthcare, focusing on diagnostic accuracy and patient outcomes...'
      },
      {
        id: '2',
        title: 'Deep Learning for Medical Image Analysis',
        journal: 'IEEE Transactions on Medical Imaging',
        year: 2022,
        volume: '41',
        issue: '8',
        abstractHighlight: 'We present a novel deep learning approach for medical image analysis that achieves state-of-the-art results in tumor detection...'
      }
    ],
    academicHistory: [
      { year: '2020', title: 'Doutorado em Ciência da Computação', institution: 'Universidade de São Paulo' },
      { year: '2016', title: 'Mestrado em Inteligência Artificial', institution: 'UNICAMP' },
      { year: '2014', title: 'Bacharelado em Ciência da Computação', institution: 'UFRJ' }
    ]
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header com botão voltar */}
      <div className="border-b border-border">
        <div className="container mx-auto px-4 py-4">
          <Button
            variant="ghost"
            onClick={() => navigate('/')}
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Voltar para busca
          </Button>
        </div>
      </div>

      <main className="container mx-auto px-4 py-8">
        {/* Informações do pesquisador */}
        <div className="flex flex-col md:flex-row gap-6 mb-8">
          <div className="flex-shrink-0">
            <img 
              src={researcher.photo} 
              alt={researcher.name}
              className="w-48 h-48 object-cover rounded-lg"
            />
          </div>
          <div className="flex-1">
            <h1 className="text-3xl font-bold mb-2">{researcher.name}</h1>
            <p className="text-xl text-muted-foreground mb-4">{researcher.title}</p>
            <Badge variant="secondary" className="text-lg px-3 py-1">
              H-Index: {researcher.hIndex}
            </Badge>
          </div>
        </div>

        {/* Resumo de pesquisa */}
        <SearchSummary
          totalResults={researcher.productions.length}
          topKeyword="machine learning"
          searchTerm={researcher.name}
        />

        {/* Produções */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Produções Científicas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {researcher.productions.map((article) => (
                <SearchResult
                  key={article.id}
                  title={article.title}
                  journal={article.journal}
                  year={article.year}
                  volume={article.volume}
                  issue={article.issue}
                  abstractHighlight={article.abstractHighlight}
                  searchTerm=""
                />
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Histórico Acadêmico */}
        <Card>
          <CardHeader>
            <CardTitle>Histórico Acadêmico</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {researcher.academicHistory.map((item, index) => (
                <div key={index} className="flex gap-4 p-4 border rounded-lg">
                  <Badge variant="outline">{item.year}</Badge>
                  <div>
                    <h3 className="font-semibold">{item.title}</h3>
                    <p className="text-muted-foreground">{item.institution}</p>
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
