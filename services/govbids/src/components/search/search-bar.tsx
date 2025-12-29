"use client";

import { useState, useTransition } from "react";
import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useSearchFilters } from "@/hooks/use-search";

export function SearchBar() {
  const [filters, setFilters] = useSearchFilters();
  const [localKeywords, setLocalKeywords] = useState(filters.keywords);
  const [isPending, startTransition] = useTransition();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    startTransition(() => {
      setFilters({ keywords: localKeywords, page: 1 });
    });
  };

  const handleClear = () => {
    setLocalKeywords("");
    startTransition(() => {
      setFilters({ keywords: "", page: 1 });
    });
  };

  return (
    <form onSubmit={handleSearch} className="flex gap-2">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          type="text"
          placeholder="Search contracts by keyword..."
          value={localKeywords}
          onChange={(e) => setLocalKeywords(e.target.value)}
          className="pl-9 pr-9"
        />
        {localKeywords && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
      <Button type="submit" disabled={isPending}>
        {isPending ? "Searching..." : "Search"}
      </Button>
    </form>
  );
}
