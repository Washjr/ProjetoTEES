import { SearchMode } from "./SearchInterface";

interface SearchToggleProps {
  searchMode: SearchMode;
  onModeChange: (mode: SearchMode) => void;
}

const SearchToggle = ({ searchMode, onModeChange }: SearchToggleProps) => {
  return (
    <div className="flex items-center justify-center">
      <div className="relative bg-slate-100 rounded-xl p-1 flex">
        <div
          className={`absolute top-1 bottom-1 rounded-lg bg-white shadow-sm transition-all duration-300 ease-out ${
            searchMode === "articles"
              ? "left-1 right-1/2 mr-0.5"
              : "right-1 left-1/2 ml-0.5"
          }`}
        />

        <button
          onClick={() => onModeChange("articles")}
          className={`relative z-10 px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
            searchMode === "articles"
              ? "text-blue-700 shadow-sm"
              : "text-slate-600 hover:text-slate-800"
          }`}
        >
          <span className="flex items-center gap-2">
            <span className="text-lg">📄</span>
            Artigos
          </span>
        </button>

        <button
          onClick={() => onModeChange("researchers")}
          className={`relative z-10 px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
            searchMode === "researchers"
              ? "text-indigo-700 shadow-sm"
              : "text-slate-600 hover:text-slate-800"
          }`}
        >
          <span className="flex items-center gap-2">
            <span className="text-lg">👨‍🔬</span>
            Pesquisadores
          </span>
        </button>
      </div>
    </div>
  );
};

export default SearchToggle;
