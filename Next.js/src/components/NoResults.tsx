
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';

interface NoResultsProps {
  searchTerm: string;
}

const NoResults = ({ searchTerm }: NoResultsProps) => {
  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardContent className="text-center py-12">
        <div className="text-6xl text-muted-foreground mb-4">🔍</div>
        <h3 className="text-xl font-semibold text-foreground mb-2">
          Nenhum resultado encontrado
        </h3>
        <p className="text-muted-foreground mb-4">
          Não encontramos nenhum documento científico para "{searchTerm}"
        </p>
        <div className="text-sm text-muted-foreground">
          <p>Tente:</p>
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>Verificar a ortografia</li>
            <li>Usar termos mais gerais</li>
            <li>Usar sinônimos ou termos relacionados</li>
            <li>Pesquisar em inglês para maior abrangência</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
};

export default NoResults;
