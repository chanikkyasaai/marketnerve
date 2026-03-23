export default function NotFound() {
    return (
        <html lang="en">
            <body style={{ background: "#030a07", color: "#00ff88", fontFamily: "monospace", display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh", flexDirection: "column", gap: 16 }}>
                <div style={{ fontSize: "4rem", fontFamily: "sans-serif" }}>404</div>
                <div style={{ fontSize: "1rem", opacity: 0.6 }}>Signal not found in the stream.</div>
                <a href="/" style={{ marginTop: 16, padding: "10px 24px", border: "1px solid rgba(0,255,136,0.4)", borderRadius: 4, color: "#00ff88", textDecoration: "none", fontSize: "0.85rem" }}>
                    ← Return to War Room
                </a>
            </body>
        </html>
    );
}
