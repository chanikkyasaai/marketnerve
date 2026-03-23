import "./globals.css";

export const metadata = {
  title: "MarketNerve",
  description: "Autonomous signal intelligence for Indian equities.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
