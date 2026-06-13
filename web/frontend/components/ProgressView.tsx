import type { JobResponse } from "@/lib/api";
import { STEPS, STATUS_DESCRIPTION, currentStepIndex } from "@/lib/status";

interface Props {
  job: JobResponse;
}

export function ProgressView({ job }: Props) {
  const stepIdx = currentStepIndex(job.status);
  const isQueued = job.status === "queued";

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-xl font-bold text-gray-800">処理中です...</h1>
      </div>

      {/* 安心メッセージ（最重要） */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-blue-800 text-sm font-medium">
          📧 このページを閉じても大丈夫です。
        </p>
        <p className="text-blue-700 text-sm mt-1">
          完成したら <strong>{job.status !== "queued" ? "メール" : "メール"}</strong> でお知らせします。
        </p>
      </div>

      {/* キュー待ちバナー */}
      {isQueued && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
          <p className="text-gray-600 text-sm">🕐 現在混み合っています。順番をお待ちください。</p>
        </div>
      )}

      {/* ステッパー */}
      {!isQueued && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <p className="text-xs text-gray-500 mb-4 font-medium">処理の進捗</p>
          <div className="space-y-0">
            {STEPS.map((step, i) => {
              const isDone = i < stepIdx;
              const isCurrent = i === stepIdx;
              const isFuture = i > stepIdx;

              return (
                <div key={step.status} className="flex items-start gap-3">
                  <div className="flex flex-col items-center">
                    <div
                      className={`w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 ${
                        isDone
                          ? "bg-green-500 text-white"
                          : isCurrent
                          ? "bg-primary text-white animate-pulse"
                          : "bg-gray-200 text-gray-400"
                      }`}
                    >
                      {isDone ? "✓" : i + 1}
                    </div>
                    {i < STEPS.length - 1 && (
                      <div
                        className={`w-0.5 h-6 ${isDone ? "bg-green-300" : "bg-gray-200"}`}
                      />
                    )}
                  </div>
                  <div className="pb-2">
                    <p
                      className={`text-sm font-medium ${
                        isCurrent ? "text-primary" : isDone ? "text-green-700" : "text-gray-400"
                      }`}
                    >
                      {step.label}
                    </p>
                    {isCurrent && (
                      <p className="text-xs text-gray-500 mt-0.5">
                        {STATUS_DESCRIPTION[step.status]}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <p className="text-center text-sm text-gray-400">
        目安: 15〜30分程度
      </p>
    </div>
  );
}
