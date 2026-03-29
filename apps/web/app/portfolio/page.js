import { MarketNerveShell } from "../../components/marketnerve-shell";
import { analyzePortfolio, getHealthData } from "../../lib/marketnerve-api.mjs";
import { PortfolioLensClient } from "../../components/portfolio-lens-client";

export default async function PortfolioPage() {
  let health = { market_status: "loading" };
  try {
    health = await getHealthData();
  } catch (e) {
    console.error("Failed to fetch health", e);
  }
  // Start with null - component will handle empty state
  const analysis = null;

  return (
    <MarketNerveShell
      marketStatus={health.market_status}
      eyebrow="Portfolio Lens"
      title="Portfolio X-Ray"
      subtitle="Session-first portfolio intelligence — overlap detection, gain tracking, and structured portfolio Q&A."
    >
      <PortfolioLensClient initialAnalysis={analysis} />
    </MarketNerveShell>
  );
}
