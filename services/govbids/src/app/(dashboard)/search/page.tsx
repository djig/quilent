import { Suspense } from "react";
import { SearchBar } from "@/components/search/search-bar";
import { SearchFilters } from "@/components/search/search-filters";
import { SearchResults } from "@/components/search/search-results";
import { Skeleton } from "@/components/ui/skeleton";
import { NuqsAdapter } from "nuqs/adapters/next/app";

export default function SearchPage() {
  return (
    <NuqsAdapter>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Search Contracts</h1>
          <p className="text-muted-foreground mt-1">
            Find government contract opportunities
          </p>
        </div>

        <div className="space-y-4">
          <Suspense fallback={<Skeleton className="h-10 w-full" />}>
            <SearchBar />
          </Suspense>

          <Suspense
            fallback={
              <div className="grid gap-4 sm:grid-cols-3">
                <Skeleton className="h-16" />
                <Skeleton className="h-16" />
                <Skeleton className="h-16" />
              </div>
            }
          >
            <SearchFilters />
          </Suspense>
        </div>

        <Suspense
          fallback={
            <div className="space-y-4">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-32" />
              ))}
            </div>
          }
        >
          <SearchResults />
        </Suspense>
      </div>
    </NuqsAdapter>
  );
}
