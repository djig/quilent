"use client";

import { useQuery } from "@tanstack/react-query";
import { useSession } from "next-auth/react";
import { parseAsString, parseAsInteger, useQueryStates } from "nuqs";
import { searchEntities, type EntityList, type SearchFilters } from "@/lib/api";

export function useSearchFilters() {
  return useQueryStates({
    keywords: parseAsString.withDefault(""),
    agency: parseAsString.withDefault(""),
    naics_code: parseAsString.withDefault(""),
    set_aside: parseAsString.withDefault(""),
    page: parseAsInteger.withDefault(1),
  });
}

export function useSearch() {
  const { data: session } = useSession();
  const [filters] = useSearchFilters();

  const limit = 20;
  const offset = (filters.page - 1) * limit;

  const searchFilters: SearchFilters = {
    keywords: filters.keywords || undefined,
    agency: filters.agency || undefined,
    naics_code: filters.naics_code || undefined,
    set_aside: filters.set_aside || undefined,
  };

  return useQuery<EntityList>({
    queryKey: ["search", searchFilters, offset, limit],
    queryFn: () =>
      searchEntities(searchFilters, { limit, offset }, session?.accessToken),
    enabled: true,
  });
}
