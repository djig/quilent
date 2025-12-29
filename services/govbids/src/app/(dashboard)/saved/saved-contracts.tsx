"use client";

import { useQuery } from "@tanstack/react-query";
import { useSession } from "next-auth/react";
import { getSavedEntities } from "@/lib/api";
import { ContractCard } from "@/components/search/contract-card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Bookmark, Search } from "lucide-react";
import Link from "next/link";

export function SavedContracts() {
  const { data: session } = useSession();

  const { data, isLoading, error } = useQuery({
    queryKey: ["saved-contracts"],
    queryFn: () => getSavedEntities({}, session?.accessToken!),
    enabled: !!session?.accessToken,
  });

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
          Failed to load saved contracts. Please try again.
        </p>
      </div>
    );
  }

  if (!data || data.data.length === 0) {
    return (
      <div className="text-center py-12">
        <Bookmark className="mx-auto h-12 w-12 text-muted-foreground" />
        <h3 className="mt-4 text-lg font-semibold">No saved contracts</h3>
        <p className="mt-2 text-muted-foreground">
          Start searching and save contracts you&apos;re interested in.
        </p>
        <Button asChild className="mt-4">
          <Link href="/search">
            <Search className="mr-2 h-4 w-4" />
            Search Contracts
          </Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        {data.total} saved contract{data.total !== 1 ? "s" : ""}
      </p>
      <div className="grid gap-4">
        {data.data.map((contract) => (
          <ContractCard key={contract.id} contract={contract} />
        ))}
      </div>
    </div>
  );
}
