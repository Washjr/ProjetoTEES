import { useState } from "react";
import SearchToggle from "./SearchToggle";
import SearchBar from "./SearchBar";

export type SearchMode = "articles" | "researchers";

interface SearchInterfaceProps {
  onSearch: (query: string, mode: SearchMode) => void;
  isLoading?: boolean;
}

const SearchInterface = ({ onSearch, isLoading = false }: SearchInterfaceProps) => {
  const [searchMode, setSearchMode] = useState<SearchMode>("articles");
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearch = () => {
    if (!searchQuery.trim()) return;
    onSearch(searchQuery, searchMode);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  const handleQuickSearch = (term: string) => {
    setSearchQuery(term);
    onSearch(term, searchMode);
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl border border-slate-200/50 p-8">
        <SearchToggle searchMode={searchMode} onModeChange={setSearchMode} />

        <div className="mt-6">
          <SearchBar
            searchQuery={searchQuery}
            searchMode={searchMode}
            onQueryChange={setSearchQuery}
            onKeyPress={handleKeyPress}
            onSearch={handleSearch}
            isLoading={isLoading}
          />
        </div>

        <div className="flex flex-wrap gap-2 mt-4">
          {searchMode === "articles" ? (
            <>
              <button 
                onClick={() => handleQuickSearch("Machine Learning")}
                className="px-3 py-1 text-sm text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
              >
                Machine Learning
              </button>
              <button 
                onClick={() => handleQuickSearch("Climate Change")}
                className="px-3 py-1 text-sm text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
              >
                Climate Change
              </button>
              <button 
                onClick={() => handleQuickSearch("Quantum Physics")}
                className="px-3 py-1 text-sm text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
              >
                Quantum Physics
              </button>
              <button 
                onClick={() => handleQuickSearch("Biotechnology")}
                className="px-3 py-1 text-sm text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
              >
                Biotechnology
              </button>
            </>
          ) : (
            <>
              <button 
                onClick={() => handleQuickSearch("Computer Science")}
                className="px-3 py-1 text-sm text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 rounded-full transition-colors"
              >
                Computer Science
              </button>
              <button 
                onClick={() => handleQuickSearch("Psychology")}
                className="px-3 py-1 text-sm text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 rounded-full transition-colors"
              >
                Psychology
              </button>
              <button 
                onClick={() => handleQuickSearch("Environmental Science")}
                className="px-3 py-1 text-sm text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 rounded-full transition-colors"
              >
                Environmental Science
              </button>
              <button 
                onClick={() => handleQuickSearch("Medicine")}
                className="px-3 py-1 text-sm text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 rounded-full transition-colors"
              >
                Medicine
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchInterface;
