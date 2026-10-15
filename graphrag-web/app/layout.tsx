import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GraphRAG para apoio à decisão | TCC UCSal",
  description: "Consulta aos estudos selecionados no mapeamento sistemático sobre GraphRAG para apoio à tomada de decisão (UCSal, 2026).",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR" className="h-full antialiased">
      <body className="min-h-full bg-stone-50 text-stone-900">{children}</body>
    </html>
  );
}
