const rows = [
  ["Market data", "MEXC Futures public market endpoints", "Connected in API"],
  ["Cross-exchange", "Binance · Bybit public market feeds", "Adapter expansion"],
  ["Metadata", "CoinGecko · CoinMarketCap enrichment", "Optional API keys"],
  ["Storage", "PostgreSQL persistent market snapshots", "Configured for deployment"],
  ["Notifications", "In-app · Browser · Email", "Delivery expansion"],
];

export default function Page() {
  return (
    <div className="space-y-5">
      <div>
        <div className="eyebrow mb-2">WORKSPACE / CONFIGURATION</div>
        <h1 className="text-2xl font-extrabold">Settings<span className="text-[#9cf56b]">.</span></h1>
        <p className="mt-1 text-xs text-[#8993a5]">Application connections and workspace preferences.</p>
      </div>
      <div className="panel divide-y divide-[#202633]">
        {rows.map((row) => (
          <div key={row[0]} className="flex flex-wrap items-center justify-between gap-3 p-4">
            <div>
              <div className="font-bold">{row[0]}</div>
              <div className="mt-1 text-xs text-[#8993a5]">{row[1]}</div>
            </div>
            <span className="tag">{row[2]}</span>
          </div>
        ))}
      </div>
      <div className="rounded-lg border border-[#34412d] bg-[#151d16] p-4 text-xs leading-5 text-[#b9d6a7]">
        Market history is stored in the project's persistent PostgreSQL volume. The API records the
        top 100 contracts by 24-hour turnover once per minute and retains seven days by default.
      </div>
      <div className="rounded-lg border border-[#66512d] bg-[#211b11] p-4 text-xs leading-5 text-[#e8c17a]">
        Optional provider API keys belong in the nordvex-api service's Railway Variables, never in
        browser storage or GitHub. Use read-only market-data credentials only; no trading or
        withdrawal permissions are required. MEXC public market data works without an API key.
      </div>
    </div>
  );
}
