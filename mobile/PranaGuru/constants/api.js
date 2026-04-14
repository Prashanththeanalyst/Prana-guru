import Constants from "expo-constants";

// Reads from app.json extra.backendUrl; falls back to localhost for local dev
export const BACKEND_URL =
  Constants.expoConfig?.extra?.backendUrl || "http://localhost:8001";

export const API = `${BACKEND_URL}/api`;
