import { MarketNerveShell } from "../../components/marketnerve-shell";
import { analyzePortfolio } from "../../lib/marketnerve-api.mjs";
import { PortfolioLensClient } from "../../components/portfolio-lens-client";

export default async function PortfolioPage() {
  const analysis = await analyzePortfolio({ use_demo_data: true });

  return (
    <MarketNerveShell
      eyebrow="Portfolio Lens"
      title="Portfolio X-Ray"
      subtitle="Session-first portfolio intelligence — overlap detection, gain tracking, and structured portfolio Q&A."
    >
      <PortfolioLensClient initialAnalysis={analysis} />
    </MarketNerveShell>
  );
}
