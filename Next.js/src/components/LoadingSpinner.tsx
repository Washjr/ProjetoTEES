
import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      <p className="mt-4 text-muted-foreground">Processando sua pesquisa...</p>
      <p className="text-sm text-muted-foreground mt-1">Analisando bases científicas</p>
    </div>
  );
};

export default LoadingSpinner;
