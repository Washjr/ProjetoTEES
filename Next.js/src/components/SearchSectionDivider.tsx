import React from "react";

interface SearchSectionDividerProps {
  title: string;
  count: number;
  icon?: string;
}

const SearchSectionDivider: React.FC<SearchSectionDividerProps> = ({
  title,
  count,
  icon = "🔍"
}) => {
  return (
    <div className="my-8">
      <div className="flex items-center justify-center">
        <div className="flex-grow h-px bg-gradient-to-r from-transparent via-slate-300 to-slate-300"></div>
        <div className="mx-6 bg-white px-4 py-2 rounded-full border border-slate-200 shadow-sm">
          <div className="flex items-center space-x-2">
            <span className="text-lg">{icon}</span>
            <span className="font-semibold text-slate-700">{title}</span>
            <span className="bg-blue-100 text-blue-800 text-sm font-medium px-2 py-1 rounded-full">
              {count}
            </span>
          </div>
        </div>
        <div className="flex-grow h-px bg-gradient-to-l from-transparent via-slate-300 to-slate-300"></div>
      </div>
    </div>
  );
};

export default SearchSectionDivider;
