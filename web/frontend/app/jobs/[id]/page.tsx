"use client";

// Next.js 14 では params は Promise ではなく直接オブジェクト。
// use(params) は Next.js 15 API なので使わない。
import { useQuery } from "@tanstack/react-query";
import { getJob } from "@/lib/api";
import { isTerminal } from "@/lib/status";
import { ProgressView } from "@/components/ProgressView";
import { DoneView } from "@/components/DoneView";
import { FailedView } from "@/components/FailedView";

export default function JobPage({ params }: { params: { id: string } }) {
  const { id } = params;

  const { data, error, isLoading } = useQuery({
    queryKey: ["job", id],
    queryFn: () => getJob(id),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status && isTerminal(status)) return false;
      return 5000;
    },
    retry: (failureCount, err) => {
      if (err instanceof Error && err.message.includes("無効")) return false;
      return failureCount < 3;
    },
  });

  if (isLoading) {
    return (
      <div className="text-center py-16 text-gray-500">
        <div className="text-4xl mb-4">⏳</div>
        <p>読み込み中...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center space-y-4">
        <p className="text-red-800">
          {error instanceof Error ? error.message : "このリンクは無効か、有効期限が切れています。"}
        </p>
        <a href="/" className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-medium">
          トップへ戻る
        </a>
      </div>
    );
  }

  if (data.status === "done") return <DoneView job={data} />;
  if (data.status === "failed") return <FailedView job={data} />;
  return <ProgressView job={data} />;
}
