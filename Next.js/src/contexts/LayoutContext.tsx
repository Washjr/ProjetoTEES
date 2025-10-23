import React, { createContext, useContext, useState, ReactNode, useMemo } from 'react';

interface LayoutContextType {
  showBackButton: boolean;
  backButtonText: string;
  className: string;
  setLayoutConfig: (config: Partial<LayoutConfig>) => void;
}

interface LayoutConfig {
  showBackButton?: boolean;
  backButtonText?: string;
  className?: string;
}

const LayoutContext = createContext<LayoutContextType | undefined>(undefined);

export const useLayout = () => {
  const context = useContext(LayoutContext);
  if (context === undefined) {
    throw new Error('useLayout must be used within a LayoutProvider');
  }
  return context;
};

interface LayoutProviderProps {
  children: ReactNode;
}

export const LayoutProvider: React.FC<LayoutProviderProps> = ({ children }) => {
  const [showBackButton, setShowBackButton] = useState(false);
  const [backButtonText, setBackButtonText] = useState("Voltar para busca");
  const [className, setClassName] = useState("");

  const setLayoutConfig = (config: LayoutConfig) => {
    if (config.showBackButton !== undefined) {
      setShowBackButton(config.showBackButton);
    }
    if (config.backButtonText !== undefined) {
      setBackButtonText(config.backButtonText);
    }
    if (config.className !== undefined) {
      setClassName(config.className);
    }
  };

  const value = useMemo(() => ({
    showBackButton,
    backButtonText,
    className,
    setLayoutConfig,
  }), [showBackButton, backButtonText, className]);

  return (
    <LayoutContext.Provider value={value}>
      {children}
    </LayoutContext.Provider>
  );
};