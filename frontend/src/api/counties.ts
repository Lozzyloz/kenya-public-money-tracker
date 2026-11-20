
import { apiRequest } from "./client";

export interface County {
  id: number;
  code: number;
  name: string;
}

export async function getCounties(): Promise<County[]> {
  return apiRequest<County[]>("/counties");
}
