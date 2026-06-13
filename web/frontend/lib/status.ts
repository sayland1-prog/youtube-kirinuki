import type { JobStatus } from "./api";

// デザインの enum-display-map.md と完全一致させること

export const STATUS_LABEL: Record<JobStatus, string> = {
  queued:       "順番待ち中",
  downloading:  "動画を準備中",
  transcribing: "音声を解析中",
  analyzing:    "見どころを選定中",
  clipping:     "動画を加工中",
  done:         "完成！",
  failed:       "処理に失敗",
};

export const STATUS_DESCRIPTION: Record<JobStatus, string> = {
  queued:       "現在混み合っています。もう少々お待ちください。",
  downloading:  "動画データを取得しています...",
  transcribing: "音声からテキストを生成しています...",
  analyzing:    "AIが盛り上がった場面を選んでいます...",
  clipping:     "縦型・横型の動画と投稿文を生成しています...",
  done:         "切り抜き動画ができました。ダウンロードしてください。",
  failed:       "処理中にエラーが発生しました。",
};

// ステッパーに表示するステップ（queued は別途キュー待ちバナーで表示）
export const STEPS: { status: JobStatus; label: string }[] = [
  { status: "downloading",  label: "動画を準備中" },
  { status: "transcribing", label: "音声を解析中" },
  { status: "analyzing",    label: "見どころを選定中" },
  { status: "clipping",     label: "動画を加工中" },
];

export function isTerminal(status: JobStatus): boolean {
  return status === "done" || status === "failed";
}

export function currentStepIndex(status: JobStatus): number {
  return STEPS.findIndex((s) => s.status === status);
}
