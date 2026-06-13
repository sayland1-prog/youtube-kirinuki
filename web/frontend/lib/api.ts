const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

// ---------- 型定義（API契約に完全一致） ----------

export type JobStatus =
  | "queued"
  | "downloading"
  | "transcribing"
  | "analyzing"
  | "clipping"
  | "done"
  | "failed";

export interface ClipItem {
  title: string;
  url_9x16: string;
  url_16x9: string;
  caption_txt_url: string;
}

export interface ProgressInfo {
  step: string | null;
  percent: number | null;
}

export interface JobResponse {
  job_id: string;
  status: JobStatus;
  progress: ProgressInfo | null;
  error_message: string | null;
  created_at: string | null;
  expires_at: string | null;
  clips: ClipItem[] | null;
}

export interface CreateJobResponse {
  job_id: string;
  status: "queued";
}

// ---------- API クライアント ----------

export async function createJob(
  youtube_url: string,
  email: string,
  agreed_terms: boolean
): Promise<CreateJobResponse> {
  const res = await fetch(`${API_BASE}/api/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ youtube_url, email, agreed_terms }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "エラーが発生しました。" }));
    throw new ApiError(res.status, err.detail ?? "エラーが発生しました。");
  }

  return res.json() as Promise<CreateJobResponse>;
}

export async function getJob(job_id: string): Promise<JobResponse> {
  const res = await fetch(`${API_BASE}/api/jobs/${job_id}`);

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "エラーが発生しました。" }));
    throw new ApiError(res.status, err.detail ?? "エラーが発生しました。");
  }

  return res.json() as Promise<JobResponse>;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}
