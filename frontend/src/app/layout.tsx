import "./globals.css";
import Nav from "@/components/Nav";
import AuroraBackground from "@/components/AuroraBackground";

export const metadata = {
  title: "ClaimLens 2.0",
  description: "Multi-agent evidence intelligence platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuroraBackground
          color="#00ffff"
          speed={1.0}
          intensity={2.0}
        />
        <Nav />
        <div className="app-content">{children}</div>
      </body>
    </html>
  );
}
