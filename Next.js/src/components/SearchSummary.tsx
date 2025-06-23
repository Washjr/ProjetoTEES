
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface SearchSummaryProps {
  totalResults: number;
  topKeyword: string;
  searchTerm: string;
}

const SearchSummary = ({ totalResults, topKeyword, searchTerm }: SearchSummaryProps) => {
  // Tags simuladas baseadas na pesquisa
  const mockTags = [
    'machine learning',
    'inteligência artificial',
    'deep learning',
    'algoritmos',
    'redes neurais',
    'diagnóstico médico',
    'imagens médicas',
    'processamento'
  ];

  const summaryText = `A busca por "${searchTerm}" retornou ${totalResults} documentos científicos relevantes. Os resultados abrangem principalmente pesquisas relacionadas a ${topKeyword} e suas aplicações em diferentes áreas. A análise dos documentos mostra uma concentração de estudos em métodos computacionais avançados e suas implementações práticas na área da saúde e medicina.`;

  return (
    <Card className="w-full max-w-4xl mx-auto mb-6 shadow-md border-0 bg-card">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl font-medium text-foreground">
            Sumário
          </CardTitle>
          <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20">
            Gerado por IA
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Coluna da esquerda - Resumo */}
          <div className="lg:col-span-2">
            <p className="text-sm text-muted-foreground leading-relaxed">
              {summaryText}
            </p>
          </div>
          
          {/* Coluna da direita - Tags */}
          <div className="lg:col-span-1">
            <h4 className="text-sm font-medium text-foreground mb-3">Tags mais relevantes</h4>
            <div className="flex flex-col gap-2">
              {mockTags.slice(0, 6).map((tag, index) => (
                <Badge 
                  key={index} 
                  variant="outline" 
                  className="justify-start text-xs py-1.5 bg-secondary/50 border-border hover:bg-secondary/70 transition-colors"
                >
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default SearchSummary;
