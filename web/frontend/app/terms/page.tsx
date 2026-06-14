import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "利用規約 | youtube-kirinuki",
};

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-3xl space-y-8 px-6 py-12">
      <div>
        <h1 className="text-2xl font-bold text-foreground mb-2">利用規約</h1>
        <p className="text-sm text-muted-foreground">最終更新: 2025年1月</p>
      </div>

      {/* 著作権・コンテンツ */}
      <section className="space-y-3">
        <h2 className="text-lg font-bold text-gray-800 border-b border-gray-200 pb-2">
          第1条（著作権・コンテンツの取り扱い）
        </h2>
        <ol className="list-decimal list-outside pl-5 space-y-3 text-sm text-gray-700 leading-relaxed">
          <li>
            本サービスは、ユーザーが入力した動画 URL の著作権状態を確認しません。
          </li>
          <li>
            ユーザーは、本サービスを利用する前に、対象動画の著作権者（配信者等）から
            切り抜き・二次利用に関する許可を得ていることを自ら確認する責任を負います。
          </li>
          <li>
            著作権者が定める切り抜きガイドライン（クレジット表記、収益化条件等）がある場合は、
            ユーザーがそれに従う責任を負います。
          </li>
          <li>
            本サービスの利用により著作権侵害が生じた場合、運営者は一切の責任を負いません。
          </li>
        </ol>
      </section>

      {/* 禁止事項 */}
      <section className="space-y-3">
        <h2 className="text-lg font-bold text-gray-800 border-b border-gray-200 pb-2">
          第2条（禁止事項）
        </h2>
        <p className="text-sm text-gray-700">ユーザーは以下の行為を行ってはなりません。</p>
        <ul className="list-disc list-outside pl-5 space-y-2 text-sm text-gray-700 leading-relaxed">
          <li>切り抜き許可を得ていない動画への本サービスの使用</li>
          <li>著作権者のガイドラインに反する形での切り抜き動画の公開・収益化</li>
          <li>本サービスへの過度な負荷をかける行為</li>
          <li>本サービスを通じた違法行為</li>
        </ul>
      </section>

      {/* 免責事項 */}
      <section className="space-y-3">
        <h2 className="text-lg font-bold text-gray-800 border-b border-gray-200 pb-2">
          第3条（免責事項）
        </h2>
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-900 leading-relaxed">
          <p className="font-semibold mb-2">本サービスはツールです。</p>
          <p>
            YouTube の動画からショート動画を自動生成する機能を提供しますが、
            その動画を使用してよいかどうかの判断はユーザー自身が行う必要があります。
          </p>
          <p className="mt-2">切り抜きを行う前に、必ず以下を確認してください：</p>
          <ul className="list-disc list-outside pl-5 mt-1 space-y-1">
            <li>配信者が切り抜きを許可しているか</li>
            <li>収益化・クレジット表記など条件があるか</li>
            <li>配信者の最新ガイドラインを確認しているか</li>
          </ul>
        </div>
      </section>

      {/* ファイルの保持期間 */}
      <section className="space-y-3">
        <h2 className="text-lg font-bold text-gray-800 border-b border-gray-200 pb-2">
          第4条（生成ファイルの保持期間）
        </h2>
        <p className="text-sm text-gray-700 leading-relaxed">
          生成された切り抜き動画ファイルは、処理完了から <strong>7日間</strong> 保持されます。
          期限を過ぎたファイルは自動的に削除されます。必要なファイルは期限内にダウンロードしてください。
        </p>
      </section>

      {/* 変更 */}
      <section className="space-y-3">
        <h2 className="text-lg font-bold text-gray-800 border-b border-gray-200 pb-2">
          第5条（規約の変更）
        </h2>
        <p className="text-sm text-gray-700 leading-relaxed">
          運営者は必要に応じて本規約を変更できます。変更後も本サービスを継続利用した場合、
          変更後の規約に同意したものとみなします。
        </p>
      </section>

      <div className="pt-4 border-t border-gray-200">
        <Link
          href="/"
          className="inline-block bg-primary text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-hover transition-colors text-sm"
        >
          ← トップに戻る
        </Link>
      </div>
      </div>
    </div>
  );
}
