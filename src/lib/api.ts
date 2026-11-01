import type { MarketResponse } from "./types";

const API = process.env.NEXT_PUBLIC_API_URL
  ? `${process.env.NEXT_PUBLIC_API_URL.replace(/\\/$/, "")}/api`
  : "/market-api";

export async function getMarket(): Promise<MarketResponse> {
  try {
    const response = await fetch(`${API}/market/screener?limit=150`, {
      cache: "no-store",
      signal: AbortSignal.timeout(7000),
    });
    if (!response.ok) throw new Error(String(response.status));
    return await response.json();
  } catch {
    return {
      source: "MEXC Futures",
      status: "degraded",
      updatedAt: new Date().toISOString(),
      items: [],
      warning: "Market API unavailable. Check the API service health and deployment logs.",
    };
  }
}

export type Candle = {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  turnover: number;
};

export async function getCandles(
  symbol: string,
  interval: string = "Min5",
): Promise<Candle[]> {
  const response = await fetch(
    `${API}/market/candles/${encodeURIComponent(symbol)}?interval=${interval}&limit=160`,
    { cache: "no-store", signal: AbortSignal.timeout(10000) },
  );
  if (!response.ok) throw new Error("Candle feed unavailable");
  const data = await response.json();
  return data.items || [];
}
