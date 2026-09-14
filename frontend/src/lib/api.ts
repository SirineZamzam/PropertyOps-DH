import type { Property } from "../types/property";

const API_URL = import.meta.env.VITE_API_URL;

export async function getProperties(): Promise<Property[]> {
  const response = await fetch(`${API_URL}/api/properties/`);

  if (!response.ok) {
    throw new Error("Failed to load properties.");
  }

  return response.json();
}