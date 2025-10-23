import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Tipo para classificação Qualis
 */
export type QualitsClassification = 'A1' | 'A2' | 'A3' | 'A4' | 'B1' | 'B2' | 'B3' | 'B4' | 'C' | 'SQ';

/**
 * Retorna a cor de classificação Qualis para a barra lateral
 * @param classification - Classificação Qualis
 * @returns Classe CSS para a cor de fundo
 */
export function getQualitsClassificationColor(classification?: QualitsClassification): string {
  switch (classification) {
    case 'A1': return 'bg-green-600';
    case 'A2': return 'bg-green-500';
    case 'A3': return 'bg-green-400';
    case 'A4': return 'bg-green-300';
    case 'B1': return 'bg-orange-600';
    case 'B2': return 'bg-orange-500';
    case 'B3': return 'bg-orange-400';
    case 'B4': return 'bg-orange-300';
    case 'C': return 'bg-red-500';
    case 'SQ': return 'bg-gray-400';
    default: return 'bg-transparent';
  }
}

/**
 * Retorna a cor de badge para classificação Qualis
 * @param qualis - Valor da classificação Qualis
 * @returns Classe CSS para cor de fundo e texto do badge
 */
export function getQualitsBadgeColor(qualis?: QualitsClassification): string {
  switch (qualis?.toUpperCase() as QualitsClassification) {
    case 'A1': return 'bg-green-600 text-white';
    case 'A2': return 'bg-green-500 text-white';
    case 'A3': return 'bg-green-400 text-white';
    case 'A4': return 'bg-green-300 text-gray-800';
    case 'B1': return 'bg-orange-600 text-white';
    case 'B2': return 'bg-orange-500 text-white';
    case 'B3': return 'bg-orange-400 text-gray-800';
    case 'B4': return 'bg-orange-300 text-gray-800';
    case 'C': return 'bg-red-500 text-white';
    case 'SQ': return 'bg-gray-400 text-white';
    default: return 'bg-gray-300 text-gray-800';
  }
}

/**
 * Formata o score de similaridade como porcentagem
 * @param score - Score de 0 a 1
 * @returns String formatada como porcentagem com 1 casa decimal
 */
export function formatSimilarityScore(score: number): string {
  return (score * 100).toFixed(1);
}
