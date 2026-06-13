import type { JobResponse } from "@/lib/api";

interface Props {
  job: JobResponse;
}

export function FailedView({ job }: Props) {
  return (
    <div className="space-y-5">
      <div className="text-center space-y-1">
        <div className="text-4xl">😔</div>
        <h1 className="text-xl font-bold text-red-700">処理に失敗しました</h1>
      </div>

      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800 text-sm">
          {job.error_message ?? "処理中にエラーが発生しました。再度お試しください。"}
        </p>
      </div>

      <p className="text-sm text-gray-500 text-center">
        ※ 同じ内容でメールもお送りしました
      </p>

      <div className="text-center">
        <a
          href="/"
          className="inline-block bg-primary text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-hover transition-colors"
        >
          もう一度試す →
        </a>
      </div>
    </div>
  );
}
