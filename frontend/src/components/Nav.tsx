"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const links = [
  { href: "/", label: "Home" },
  { href: "/investigate", label: "Investigate" },
  { href: "/report/sample", label: "Sample Report" },
];

export default function Nav() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [theme, setTheme] = useState<"aurora" | "coral" | "mint">("aurora");

  useEffect(() => {
    const savedTheme = window.localStorage.getItem("claimlens-theme") as "aurora" | "coral" | "mint" | null;
    if (savedTheme) setTheme(savedTheme);
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem("claimlens-theme", theme);
  }, [theme]);

  return (
    <>
      <nav className="site-nav">
      <Link href="/" className="brand-mark">
        <span className="brand-icon">⌕</span>
        <span>ClaimLens</span>
      </Link>
      <div className="nav-center">
        {links.map((l) => (
          <Link key={l.href} href={l.href} className="nav-link">
            {l.label}
          </Link>
        ))}
      </div>
      <div className="nav-actions">
        <span className="live-status"><span /> Live workspace</span>
        <button type="button" className="nav-menu-button" onClick={() => setSidebarOpen(true)} aria-label="Open appearance settings">
          <span />
          <span />
          <span />
        </button>
      </div>
      </nav>

      <div className={`sidebar-backdrop ${sidebarOpen ? "is-open" : ""}`} onClick={() => setSidebarOpen(false)} />
      <aside className={`settings-sidebar ${sidebarOpen ? "is-open" : ""}`} aria-hidden={!sidebarOpen}>
        <div className="sidebar-heading">
          <div>
            <span className="eyebrow">Workspace controls</span>
            <h2>Shape your lens</h2>
          </div>
          <button type="button" className="sidebar-close" onClick={() => setSidebarOpen(false)} aria-label="Close appearance settings">×</button>
        </div>

        <div className="sidebar-section">
          <span className="sidebar-label">Accent atmosphere</span>
          <div className="theme-options">
            {[
              ["aurora", "Aurora", "Electric blue"],
              ["coral", "Ember", "Coral signal"],
              ["mint", "Verdant", "Mint signal"],
            ].map(([value, label, description]) => (
              <button key={value} type="button" className={`theme-option ${theme === value ? "selected" : ""}`} onClick={() => setTheme(value as typeof theme)}>
                <span className={`theme-swatch ${value}`} />
                <span><strong>{label}</strong><small>{description}</small></span>
                {theme === value && <span className="theme-check">✓</span>}
              </button>
            ))}
          </div>
        </div>

        <div className="sidebar-note">
          <span className="mini-tag">Designed for focus</span>
          <p>Keep the interface quiet while ClaimLens traces the signal through every source.</p>
        </div>
      </aside>
    </>
  );
}
