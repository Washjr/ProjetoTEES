
import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ExternalLink } from 'lucide-react';

interface ArticleData {
  id: string;
  title: string;
  journal: string;
  year: number;
  volume?: string;
  issue?: string;
  abstract: string;
  doi?: string;
  authors: Array<{ id: string; name: string }>;
  tags: string[];
}

interface ArticleOverlayProps {
  article: ArticleData | null;
  isOpen: boolean;
  onClose: () => void;
  onAuthorClick: (authorId: string) => void;
}

const ArticleOverlay = ({ article, isOpen, onClose, onAuthorClick }: ArticleOverlayProps) => {
  if (!article) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl leading-tight pr-8">
            {article.title}
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Informações da publicação */}
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline">{article.year}</Badge>
            <span className="text-sm text-muted-foreground">{article.journal}</span>
            {article.volume && (
              <span className="text-sm text-muted-foreground">Vol. {article.volume}</span>
            )}
            {article.issue && (
              <span className="text-sm text-muted-foreground">Issue {article.issue}</span>
            )}
          </div>

          {/* Autores */}
          <div>
            <h3 className="font-semibold mb-2">Autores:</h3>
            <div className="flex flex-wrap gap-2">
              {article.authors.map((author) => (
                <Button
                  key={author.id}
                  variant="link"
                  className="p-0 h-auto text-primary hover:underline"
                  onClick={() => onAuthorClick(author.id)}
                >
                  {author.name}
                </Button>
              ))}
            </div>
          </div>

          {/* Abstract */}
          <div>
            <h3 className="font-semibold mb-2">Abstract:</h3>
            <p className="text-sm leading-relaxed text-muted-foreground">
              {article.abstract}
            </p>
          </div>

          {/* Tags */}
          {article.tags.length > 0 && (
            <div>
              <h3 className="font-semibold mb-2">Tags:</h3>
              <div className="flex flex-wrap gap-2">
                {article.tags.map((tag, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* DOI */}
          {article.doi && (
            <div>
              <h3 className="font-semibold mb-2">DOI:</h3>
              <Button variant="outline" size="sm" className="gap-2">
                <ExternalLink className="h-3 w-3" />
                {article.doi}
              </Button>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ArticleOverlay;
