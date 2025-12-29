"use client";

import { useSearch, useSearchFilters } from "@/hooks/use-search";
import { ContractCard } from "./contract-card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, FileX } from "lucide-react";
import { useTransition } from "react";

export function SearchResults() {
  const { data, isLoading, error } = useSearch();
  const [filters, setFilters] = useSearchFilters();
  const [isPending, startTransition] = useTransition();

  const limit = 20;
  const totalPages = data ? Math.ceil(data.total / limit) : 0;

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="rounded-lg border p-4 space-y-3">
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="h-4 w-1/4" />
            <div className="flex gap-2">
              <Skeleton className="h-5 w-24" />
              <Skeleton className="h-5 w-20" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive">
          Failed to load results. Please try again.
        </p>
      </div>
    );
  }

  if (!data || data.data.length === 0) {
    return (
      <div className="text-center py-12">
        <FileX className="mx-auto h-12 w-12 text-muted-foreground" />
        <h3 className="mt-4 text-lg font-semibold">No contracts found</h3>
        <p className="mt-2 text-muted-foreground">
          Try adjusting your search filters or keywords.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>
          Showing {data.offset + 1}-{Math.min(data.offset + limit, data.total)} of{" "}
          {data.total} results
        </span>
        <span>Page {filters.page} of {totalPages}</span>
      </div>

      <div className="grid gap-4">
        {data.data.map((contract) => (
          <ContractCard key={contract.id} contract={contract} />
        ))}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={filters.page <= 1 || isPending}
            onClick={() =>
              startTransition(() => {
                setFilters({ page: filters.page - 1 });
              })
            }
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Previous
          </Button>
          <span className="text-sm text-muted-foreground px-4">
            Page {filters.page} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={filters.page >= totalPages || isPending}
            onClick={() =>
              startTransition(() => {
                setFilters({ page: filters.page + 1 });
              })
            }
          >
            Next
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      )}
    </div>
  );
}
