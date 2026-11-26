export function getApiError(error: unknown, fallback: string, fields = ["detail", "message"]): string {
  if (!error || typeof error !== "object" || !("data" in error)) return fallback;
  const data = error.data;
  if (!data || typeof data !== "object") return fallback;

  for (const field of fields) {
    const value = (data as Record<string, unknown>)[field];
    if (typeof value === "string" && value) return value;
    if (Array.isArray(value) && typeof value[0] === "string") return value[0];
  }
  return fallback;
}
