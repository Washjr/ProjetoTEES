
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import SearchSummary from '@/components/SearchSummary';
import SearchResult from '@/components/SearchResult';
import { ResearcherProfileData } from '@/types/researcher';
import { ApiService } from '@/services/apiService';

const Researcher = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [researcherProfile, setResearcherProfile] = useState<ResearcherProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResearcherProfile = async () => {
      if (!id) {
        setError('ID do pesquisador não fornecido');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const profile = await ApiService.getResearcherProfile(id);
        
        if (!profile) {
          setError('Pesquisador não encontrado');
        } else {
          setResearcherProfile(profile);
        }
      } catch (err) {
        setError('Erro ao carregar dados do pesquisador');
        console.error('Erro ao buscar perfil do pesquisador:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchResearcherProfile();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Carregando perfil do pesquisador...</p>
        </div>
      </div>
    );
  }

  if (error || !researcherProfile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-slate-800 mb-4">Erro</h2>
          <p className="text-slate-600 mb-4">{error || 'Pesquisador não encontrado'}</p>
          <Button onClick={() => navigate('/')} className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Voltar para busca
          </Button>
        </div>
      </div>
    );
  }

  const { researcher, productions } = researcherProfile;
  // const { academicHistory } = researcherProfile; // Comentado - não implementado no backend ainda

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
          totalResults={productions.length}
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
              {productions.map((article) => (
                <SearchResult
                  key={article.id}
                  title={article.title}
                  journal={article.journal}
                  year={article.year}
                  qualis={article.qualis}
                  abstract={article.abstract}
                  searchTerm=""
                />
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Histórico Acadêmico - Comentado pois não será implementado agora no backend */}
        {/* <Card className="bg-white/70 backdrop-blur-sm border-slate-200/50 shadow-sm">
          <CardHeader>
            <CardTitle className="text-slate-800">Histórico Acadêmico</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {academicHistory.map((item, index) => (
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
        </Card> */}
      </main>
    </div>
  );
};

export default Researcher;
