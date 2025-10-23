import React from 'react';
import Header from './Header';

interface LayoutProps {
  children: React.ReactNode;
  showBackButton?: boolean;
  backButtonText?: string;
  className?: string;
}

const Layout: React.FC<LayoutProps> = ({ 
  children, 
  showBackButton = false, 
  backButtonText = "Voltar para busca",
  className = "" 
}) => {
  return (
    <div className={`min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 ${className}`}>
      <Header 
        showBackButton={showBackButton} 
        backButtonText={backButtonText} 
      />
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
};

export default Layout;