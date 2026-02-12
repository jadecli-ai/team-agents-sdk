import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "jadecli - Agent Task Dashboard",
  description: "Multi-agent task tracking and activity monitoring",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-950 text-gray-100 min-h-screen antialiased">
        <header className="border-b border-gray-800 px-6 py-4">
          <nav className="flex items-center gap-8 max-w-7xl mx-auto">
            <h1 className="text-lg font-semibold tracking-tight">
              jadecli<span className="text-emerald-400">.com</span>
            </h1>
            <a href="/" className="text-sm text-gray-400 hover:text-gray-200">
              Dashboard
            </a>
            <a
              href="/tasks"
              className="text-sm text-gray-400 hover:text-gray-200"
            >
              Tasks
            </a>
            <a
              href="/agents"
              className="text-sm text-gray-400 hover:text-gray-200"
            >
              Agents
            </a>
          </nav>
        </header>
        <main className="max-w-7xl mx-auto px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
