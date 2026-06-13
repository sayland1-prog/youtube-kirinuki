import type { ClipItem, JobResponse } from "@/lib/api";

interface Props {
  job: JobResponse;
}

function formatExpiresAt(isoStr: string | null): string {
  if (!isoStr) return "1週間";
  const d = new Date(isoStr);
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`;
}

function ClipCard({ clip, index }: { clip: ClipItem; index: number }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 space-y-3">
      <p className="font-medium text-gray-800">
        {index + 1}. {clip.title}
      </p>
      <div className="flex flex-wrap gap-2">
        <a
          href={clip.url_9x16}
          download
          className="bg-primary text-white text-sm px-4 py-2 rounded-lg font-medium hover:bg-primary-hover transition-colors"
        >
          ↓ 縦型 (9:16)
        </a>
        <a
          href={clip.url_16x9}
          download
          className="bg-primary text-white text-sm px-4 py-2 rounded-lg font-medium hover:bg-primary-hover transition-colors"
        >
          ↓ 横型 (16:9)
        </a>
        <a
          href={clip.caption_txt_url}
          download
          className="border border-gray-300 text-gray-700 text-sm px-4 py-2 rounded-lg font-medium hover:bg-gray-50 transition-colors"
        >
          ↓ 投稿文
        </a>
      </div>
    </div>
  );
}

export function DoneView({ job }: Props) {
  const expiresLabel = formatExpiresAt(job.expires_at);

  return (
    <div className="space-y-5">
      <div className="text-center space-y-1">
        <div className="text-4xl">🎉</div>
        <h1 className="text-2xl font-bold text-green-700">完成しました！</h1>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-center">
        <p className="text-amber-800 text-sm">
          ⚠️ ダウンロードリンクは <strong>{expiresLabel}</strong> まで有効です
        </p>
      </div>

      <div className="space-y-3">
        {(job.clips ?? []).map((clip, i) => (
          <ClipCard key={i} clip={clip} index={i} />
        ))}
      </div>

      <div className="text-center pt-2">
        <a
          href="/"
          className="inline-block bg-primary text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-hover transition-colors"
        >
          別の動画を切り抜く →
        </a>
      </div>
    </div>
  );
}
