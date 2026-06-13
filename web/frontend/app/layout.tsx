// Server Component（"use client" を置かない）
import type { Metadata } from "next";
import { Providers } from "./providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "切り抜き自動生成 | youtube-kirinuki",
  description: "YouTubeのURLを貼るだけ。切り抜きショート、30分で完成。",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body className="bg-gray-50 text-gray-900 font-sans">
        <Providers>
          <div className="min-h-screen">
            <header className="bg-white border-b border-gray-200 h-14 flex items-center px-4">
              <a href="/" className="font-bold text-blue-600 text-lg">
                ✂️ kirinuki
              </a>
            </header>
            <main className="py-8 px-4">
              <div className="max-w-xl mx-auto">{children}</div>
            </main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
