
import React from 'react';

const SearchHeader = () => {
  return (
    <header className="w-full bg-background border-b border-border">
      <div className="container mx-auto px-4 py-6">
        <h1 className="text-3xl font-bold text-foreground text-center">
          Pesquisa Científica
        </h1>
        <p className="text-muted-foreground text-center mt-2">
          Explore o conhecimento científico mundial
        </p>
      </div>
    </header>
  );
};

export default SearchHeader;
