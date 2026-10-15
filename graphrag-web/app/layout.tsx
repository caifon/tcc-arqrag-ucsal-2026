import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GraphRAG para Apoio à Decisão · TCC UCSal 2026",
  description:
    "Sistema de apoio à decisão baseado em GraphRAG sobre estudos selecionados em mapeamento sistemático da literatura (UCSal 2026).",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className="h-full scroll-smooth antialiased">
      <body className="min-h-full bg-slate-50 font-sans text-slate-900 selection:bg-teal-100 selection:text-teal-900">
        {children}
      </body>
    </html>
  );
}
