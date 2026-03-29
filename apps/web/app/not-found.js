import Link from "next/link";

export default function NotFound() {
  return (
    <html lang="en">
      <body style={{
        background: "#09090B",
        color: "#F1F2F7",
        fontFamily: "'Inter', system-ui, sans-serif",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        flexDirection: "column",
        gap: 16,
        padding: 24,
      }}>
        <div style={{
          fontSize: "72px",
          fontWeight: 800,
          letterSpacing: "-0.04em",
          color: "#1A1C22",
          lineHeight: 1,
        }}>404</div>
        <div style={{
          fontSize: "16px",
          fontWeight: 500,
          color: "#8C8FA3",
          marginBottom: 8,
        }}>Signal not found in the stream.</div>
        <a href="/" style={{
          padding: "8px 20px",
          border: "1px solid rgba(255,255,255,0.08)",
          borderRadius: 8,
          color: "#5B6AF0",
          textDecoration: "none",
          fontSize: "13px",
          fontFamily: "monospace",
          transition: "all 0.15s",
        }}>
          ← Return to Overview
        </a>
      </body>
    </html>
  );
}
