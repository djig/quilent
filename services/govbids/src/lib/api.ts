const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Types matching FastAPI backend schemas
export interface Entity {
  id: string;
  product_id: string;
  source_id: string;
  entity_type: string;
  title: string;
  source_url: string | null;
  data: Record<string, unknown>;
  published_at: string | null;
  summary: string | null;
  created_at: string;
}

export interface EntityList {
  data: Entity[];
  total: number;
  limit: number;
  offset: number;
}

export interface SearchFilters {
  keywords?: string;
  agency?: string;
  naics_code?: string;
  set_aside?: string;
  deadline_after?: string;
  deadline_before?: string;
}

export interface User {
  id: string;
  email: string;
  name: string | null;
  created_at: string;
}

class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {},
  accessToken?: string
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-Product-ID": "gov",
    ...((options.headers as Record<string, string>) || {}),
  };

  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new ApiError(response.status, error.detail || "Request failed");
  }

  return response.json();
}

// Entity endpoints
export async function getEntities(
  params: {
    limit?: number;
    offset?: number;
    entity_type?: string;
  } = {},
  accessToken?: string
): Promise<EntityList> {
  const searchParams = new URLSearchParams();
  if (params.limit) searchParams.set("limit", params.limit.toString());
  if (params.offset) searchParams.set("offset", params.offset.toString());
  if (params.entity_type) searchParams.set("entity_type", params.entity_type);

  const queryString = searchParams.toString();
  const endpoint = `/api/entities/${queryString ? `?${queryString}` : ""}`;

  return fetchApi<EntityList>(endpoint, {}, accessToken);
}

export async function getEntity(id: string, accessToken?: string): Promise<Entity> {
  return fetchApi<Entity>(`/api/entities/${id}`, {}, accessToken);
}

export async function searchEntities(
  filters: SearchFilters,
  pagination: { limit?: number; offset?: number } = {},
  accessToken?: string
): Promise<EntityList> {
  const searchParams = new URLSearchParams();

  if (filters.keywords) searchParams.set("keywords", filters.keywords);
  if (filters.agency) searchParams.set("agency", filters.agency);
  if (filters.naics_code) searchParams.set("naics_code", filters.naics_code);
  if (filters.set_aside) searchParams.set("set_aside", filters.set_aside);
  if (filters.deadline_after) searchParams.set("deadline_after", filters.deadline_after);
  if (filters.deadline_before) searchParams.set("deadline_before", filters.deadline_before);
  if (pagination.limit) searchParams.set("limit", pagination.limit.toString());
  if (pagination.offset) searchParams.set("offset", pagination.offset.toString());

  const queryString = searchParams.toString();
  const endpoint = `/api/search${queryString ? `?${queryString}` : ""}`;

  return fetchApi<EntityList>(endpoint, {}, accessToken);
}

// Saved entities endpoints
export async function saveEntity(id: string, accessToken: string): Promise<void> {
  await fetchApi(`/api/entities/${id}/save`, { method: "POST" }, accessToken);
}

export async function unsaveEntity(id: string, accessToken: string): Promise<void> {
  await fetchApi(`/api/entities/${id}/save`, { method: "DELETE" }, accessToken);
}

export async function getSavedEntities(
  pagination: { limit?: number; offset?: number } = {},
  accessToken: string
): Promise<EntityList> {
  const searchParams = new URLSearchParams();
  if (pagination.limit) searchParams.set("limit", pagination.limit.toString());
  if (pagination.offset) searchParams.set("offset", pagination.offset.toString());

  const queryString = searchParams.toString();
  const endpoint = `/api/entities/saved/list${queryString ? `?${queryString}` : ""}`;

  return fetchApi<EntityList>(endpoint, {}, accessToken);
}

// AI endpoints
export async function summarizeEntity(
  id: string,
  accessToken: string
): Promise<{ summary: string; cached: boolean }> {
  return fetchApi(`/api/ai/${id}/summarize`, { method: "POST" }, accessToken);
}

export async function askAboutEntity(
  id: string,
  question: string,
  accessToken: string
): Promise<{ answer: string }> {
  return fetchApi(
    `/api/ai/${id}/ask`,
    {
      method: "POST",
      body: JSON.stringify({ question }),
    },
    accessToken
  );
}

// Auth endpoints (for server-side use)
export async function getCurrentUser(accessToken: string): Promise<User> {
  return fetchApi<User>("/api/auth/me", {}, accessToken);
}

export { ApiError };
