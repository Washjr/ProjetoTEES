import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArticleData, SemanticSearchResult } from "@/types";

export const useArticleOverlay = () => {
  const navigate = useNavigate();
  const [selectedArticle, setSelectedArticle] = useState<ArticleData | null>(null);
  const [isOverlayOpen, setIsOverlayOpen] = useState(false);

  const handleArticleClick = (article: ArticleData) => {
    setSelectedArticle(article);
    setIsOverlayOpen(true);
  };

  const handleSemanticResultClick = (semanticResult: SemanticSearchResult) => {
    setSelectedArticle(semanticResult.documento);
    setIsOverlayOpen(true);
  };

  const handleAuthorClick = (authorId: string) => {
    setIsOverlayOpen(false);
    navigate(`/researcher/${authorId}`);
  };

  const closeOverlay = () => {
    setIsOverlayOpen(false);
  };

  return {
    // States
    selectedArticle,
    isOverlayOpen,
    
    // Actions
    handleArticleClick,
    handleSemanticResultClick,
    handleAuthorClick,
    closeOverlay,
  };
};