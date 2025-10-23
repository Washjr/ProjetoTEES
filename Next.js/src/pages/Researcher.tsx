
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { ChevronDown, ChevronUp } from 'lucide-react';
import Layout from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import SearchResult from '@/components/SearchResult';
import { ResearcherProfileData, ResumeData } from '@/types/researcher';
import { ApiService } from '@/services/apiService';

const Researcher = () => {
  const { id } = useParams();
  const [researcherProfile, setResearcherProfile] = useState<ResearcherProfileData | null>(null);
  const [resumeData, setResumeData] = useState<ResumeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingResume, setLoadingResume] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showResume, setShowResume] = useState(false);

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

  const handleToggleResume = async () => {
    if (!showResume && !resumeData && id) {
      setLoadingResume(true);
      try {
        const summary = await ApiService.getResearcherSummary(id);
        if (summary) {
          setResumeData(summary);
        }
      } catch (err) {
        console.error('Erro ao buscar resumo do pesquisador:', err);
      } finally {
        setLoadingResume(false);
      }
    }
    setShowResume(!showResume);
  };

  if (loading) {
    return (
      <Layout showBackButton={true} backButtonText="Voltar para busca">
        <div className="flex items-center justify-center min-h-[50vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-slate-600">Carregando perfil do pesquisador...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error || !researcherProfile) {
    return (
      <Layout showBackButton={true} backButtonText="Voltar para busca">
        <div className="flex items-center justify-center min-h-[50vh]">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-slate-800 mb-4">Erro</h2>
            <p className="text-slate-600 mb-4">{error || 'Pesquisador não encontrado'}</p>
          </div>
        </div>
      </Layout>
    );
  }

  const { researcher, productions } = researcherProfile;

  return (
    <Layout showBackButton={true} backButtonText="Voltar para busca">
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
        <Card className="mb-8 bg-white/70 backdrop-blur-sm border-slate-200/50 shadow-sm">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CardTitle className="text-slate-800">Resumo e Tags</CardTitle>
                <Badge variant="outline" className="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200 text-purple-700 text-xs">
                  Gerado por IA
                </Badge>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleToggleResume}
                className="gap-2 text-slate-600 hover:text-slate-800"
                disabled={loadingResume}
              >
                {loadingResume ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-slate-600"></div>
                ) : showResume ? (
                  <>
                    Ocultar <ChevronUp className="h-4 w-4" />
                  </>
                ) : (
                  <>
                    Mostrar <ChevronDown className="h-4 w-4" />
                  </>
                )}
              </Button>
            </div>
          </CardHeader>
          {showResume && resumeData && (
            <CardContent className="space-y-4">
              {resumeData.resumo_ia && (
                <div>
                  <h3 className="font-semibold text-slate-800 mb-2">Resumo da Pesquisa</h3>
                  <p className="text-slate-600 leading-relaxed">{resumeData.resumo_ia}</p>
                </div>
              )}
              {resumeData.tags && resumeData.tags.length > 0 && (
                <div>
                  <h3 className="font-semibold text-slate-800 mb-2">Tags Principais</h3>
                  <div className="flex flex-wrap gap-2">
                    {resumeData.tags.map((tag, index) => (
                      <Badge key={index} variant="secondary" className="bg-blue-100 text-blue-800 border-blue-200">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          )}
        </Card>

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
      </Layout>
  );
};

export default Researcher;
