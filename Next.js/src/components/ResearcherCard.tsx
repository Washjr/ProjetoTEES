
import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface ResearcherCardProps {
  id: string;
  name: string;
  title: string;
  hIndex: number;
  photo: string;
  onClick: (id: string) => void;
}

const ResearcherCard = ({ id, name, title, hIndex, photo, onClick }: ResearcherCardProps) => {
  return (
    <Card 
      className="relative overflow-hidden cursor-pointer hover:shadow-lg transition-all duration-200 aspect-[4/3] group"
      onClick={() => onClick(id)}
    >
      <div className="relative w-full h-full">
        <img 
          src={photo} 
          alt={name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
        />
        
        {/* H-Index badge */}
        <Badge 
          variant="secondary" 
          className="absolute top-2 right-2 bg-background/90 text-foreground"
        >
          H-Index: {hIndex}
        </Badge>
        
        {/* Name and title overlay */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
          <h3 className="text-white font-semibold text-lg leading-tight">{name}</h3>
          <p className="text-white/90 text-sm">{title}</p>
        </div>
      </div>
    </Card>
  );
};

export default ResearcherCard;
