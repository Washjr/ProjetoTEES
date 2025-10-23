import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface HeaderProps {
  showBackButton?: boolean;
  backButtonText?: string;
}

const Header: React.FC<HeaderProps> = ({ 
  showBackButton = false, 
  backButtonText = "Voltar para busca" 
}) => {
  const navigate = useNavigate();

  return (
    <header className="border-b border-slate-200/50 bg-white/70 backdrop-blur-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <button 
            className="flex items-center space-x-3 cursor-pointer hover:opacity-80 transition-opacity bg-transparent border-none"
            onClick={() => navigate('/')}
            type="button"
          >
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">AE</span>
            </div>
            <span className="font-semibold text-slate-800">
              Pesquisa Acadêmica
            </span>
          </button>
          
          {showBackButton && (
            <Button
              variant="ghost"
              onClick={() => navigate('/')}
              className="gap-2 text-slate-600 hover:text-slate-800"
            >
              <ArrowLeft className="h-4 w-4" />
              {backButtonText}
            </Button>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;