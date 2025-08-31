import React from "react";

interface FilterDisplayProps {
  filterInterface: string;
  contentQuery: string;
}

const FilterDisplay: React.FC<FilterDisplayProps> = ({ filterInterface, contentQuery }) => {
  // Função para dividir filtros em componentes individuais
  const parseFilters = (filterText: string) => {
    if (!filterText) return [];
    
    // Dividir por " E " (AND) para separar filtros
    const filters = filterText.split(' E ').map(filter => filter.trim());
    return filters;
  };

  const filters = parseFilters(filterInterface);

  return (
    <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-slate-200/50 shadow-sm p-4 mb-6">
      <div className="flex items-start space-x-3">
        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
          <span className="text-blue-600 text-sm font-semibold">🔍</span>
        </div>
        <div className="flex-1">
          <div className="mb-3">
            <span className="text-sm font-medium text-slate-700">
              Busca Realizada para o termo:{" "}
              <span className="font-semibold text-slate-800">"{contentQuery}"</span>
            </span>
          </div>
          
          {filters.length > 0 && (
            <div>
              <span className="text-sm font-medium text-slate-600 block mb-2">Filtros Aplicados:</span>
              <div className="flex flex-wrap gap-2">
                {filters.map((filter, index) => (
                  <div
                    key={`filter-${filter}-${index}`}
                    className="bg-blue-50 border border-blue-200 rounded-lg px-3 py-2"
                  >
                    <span className="text-sm text-blue-700">{filter}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FilterDisplay;
