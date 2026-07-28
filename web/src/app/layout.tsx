import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Synkora — AI-Powered Software Evolution Intelligence",
  description:
    "Analyze GitHub repositories to understand code evolution, architecture, technical debt, and more with AI-powered insights.",
  keywords: [
    "code analysis",
    "software evolution",
    "AI developer tools",
    "technical debt",
    "architecture visualization",
    "knowledge graph",
  ],
  authors: [{ name: "Synkora Team" }],
  openGraph: {
    title: "Synkora — AI-Powered Software Evolution Intelligence",
    description:
      "Understand. Analyze. Evolve. Deep code intelligence for modern engineering teams.",
    type: "website",
    locale: "en_US",
    siteName: "Synkora",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
