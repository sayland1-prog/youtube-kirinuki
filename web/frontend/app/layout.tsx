// Server Component（"use client" を置かない）
import type { Metadata } from "next";
import { Providers } from "./providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "kirinuki — URLを貼るだけ。切り抜きショート、30分で完成。",
  description: "文字起こし・選定・字幕・投稿文まで全自動。切り抜き許可をもらったら、あとはURLだけ。",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body className="bg-background text-foreground font-sans antialiased">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
