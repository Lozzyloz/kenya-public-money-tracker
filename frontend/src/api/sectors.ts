
import { apiRequest } from "./client";

export interface Sector {
  id: number;
  name: string;
}

export async function getSectors(): Promise<Sector[]> {
  return apiRequest<Sector[]>("/sectors");
}
