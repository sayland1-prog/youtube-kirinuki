"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useState } from "react";
import { Scissors, FileText, Captions, Send, ArrowRight, Link, Mail } from "lucide-react";
import { ApiError, createJob } from "@/lib/api";

const schema = z.object({
  youtube_url: z
    .string()
    .min(1, "YouTubeの動画URLを入力してください")
    .regex(
      /^https?:\/\/(www\.)?(youtube\.com\/watch\?.*v=[\w-]+|youtu\.be\/[\w-]+)/i,
      "YouTubeの動画URLを入力してください（例: https://www.youtube.com/watch?v=...）"
    ),
  email: z
    .string()
    .min(1, "メールアドレスを入力してください")
    .email("正しいメールアドレスの形式で入力してください"),
  agreed_terms: z.literal(true, {
    errorMap: () => ({ message: "利用規約に同意してください" }),
  }),
});

type FormValues = z.infer<typeof schema>;

const steps = [
  { icon: FileText, label: "文字起こし" },
  { icon: Scissors, label: "選定" },
  { icon: Captions, label: "字幕" },
  { icon: Send, label: "投稿文" },
];

export default function HomePage() {
  const router = useRouter();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const agreed = watch("agreed_terms");

  const onSubmit = async (data: FormValues) => {
    setServerError(null);
    try {
      const res = await createJob(data.youtube_url, data.email, data.agreed_terms);
      router.push(`/jobs/${res.job_id}`);
    } catch (err) {
      if (err instanceof ApiError && err.status === 429) {
        setServerError("現在混み合っています。少し時間をおいてから再度お試しください。");
      } else if (err instanceof Error) {
        setServerError(err.message);
      } else {
        setServerError("エラーが発生しました。再度お試しください。");
      }
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="mx-auto flex max-w-3xl items-center gap-2 px-6 py-6">
        <span className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Scissors aria-hidden="true" className="size-4" />
        </span>
        <span className="text-lg font-semibold tracking-tight text-foreground">kirinuki</span>
      </header>

      <div className="mx-auto max-w-3xl px-6 pb-20 pt-8 sm:pt-14">
        <section className="flex flex-col items-start gap-6">
          <span className="inline-flex items-center rounded-full border border-border bg-secondary/60 px-3 py-1 text-xs font-medium text-muted-foreground">
            登録不要・無料でお試しいただけます
          </span>

          <h1 className="text-balance text-4xl font-bold leading-tight tracking-tight text-foreground sm:text-5xl">
            URLを貼るだけで切り抜きショートが
            <span className="text-primary">30分</span>で完成
          </h1>

          <div className="flex flex-col gap-1 text-pretty text-base leading-relaxed text-muted-foreground sm:text-lg">
            <p>文字起こし・選定・字幕・投稿文まで全自動。</p>
            <p>切り抜き許可をもらったら、あとはURLだけ。</p>
          </div>

          <ul className="flex list-none flex-wrap gap-2 pt-1 p-0 m-0">
            {steps.map((step) => (
              <li
                key={step.label}
                className="inline-flex items-center gap-1.5 rounded-full bg-secondary px-3 py-1.5 text-sm font-medium text-secondary-foreground"
              >
                <step.icon aria-hidden="true" className="size-4 text-primary" />
                {step.label}
              </li>
            ))}
          </ul>
        </section>

        <section className="mt-10 rounded-2xl border border-border bg-card p-6 shadow-sm sm:mt-12 sm:p-8">
          {serverError && (
            <div className="mb-5 rounded-xl bg-red-50 border border-red-200 p-4 text-red-800 text-sm">
              {serverError}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-5" noValidate>
            {/* YouTube URL */}
            <div className="flex flex-col gap-2">
              <label htmlFor="youtube-url" className="text-sm font-medium text-foreground">
                YouTube の URL
              </label>
              <div className="relative">
                <Link
                  aria-hidden="true"
                  className="pointer-events-none absolute left-3.5 top-1/2 size-5 -translate-y-1/2 text-muted-foreground"
                />
                <input
                  {...register("youtube_url")}
                  id="youtube-url"
                  type="url"
                  inputMode="url"
                  placeholder="https://www.youtube.com/watch?v=..."
                  className={`w-full rounded-xl border bg-background py-3 pl-11 pr-4 text-base text-foreground placeholder:text-muted-foreground transition focus:outline-none focus:ring-4 focus:ring-primary/15 ${
                    errors.youtube_url
                      ? "border-red-500 focus:border-red-500"
                      : "border-border focus:border-primary"
                  }`}
                />
              </div>
              {errors.youtube_url && (
                <p className="text-red-600 text-sm">{errors.youtube_url.message}</p>
              )}
            </div>

            {/* メールアドレス */}
            <div className="flex flex-col gap-2">
              <label htmlFor="email" className="text-sm font-medium text-foreground">
                メールアドレス
              </label>
              <div className="relative">
                <Mail
                  aria-hidden="true"
                  className="pointer-events-none absolute left-3.5 top-1/2 size-5 -translate-y-1/2 text-muted-foreground"
                />
                <input
                  {...register("email")}
                  id="email"
                  type="email"
                  inputMode="email"
                  placeholder="you@example.com"
                  className={`w-full rounded-xl border bg-background py-3 pl-11 pr-4 text-base text-foreground placeholder:text-muted-foreground transition focus:outline-none focus:ring-4 focus:ring-primary/15 ${
                    errors.email
                      ? "border-red-500 focus:border-red-500"
                      : "border-border focus:border-primary"
                  }`}
                />
              </div>
              {errors.email && (
                <p className="text-red-600 text-sm">{errors.email.message}</p>
              )}
            </div>

            {/* 利用規約同意 */}
            <div className="flex flex-col gap-2">
              <label
                htmlFor="agreed_terms"
                className="flex cursor-pointer items-start gap-3 rounded-xl bg-secondary/60 p-4 text-sm leading-relaxed text-muted-foreground"
              >
                <input
                  {...register("agreed_terms")}
                  id="agreed_terms"
                  type="checkbox"
                  className="mt-0.5 size-5 shrink-0 cursor-pointer rounded border-border accent-primary"
                />
                <span>
                  切り抜き許可のある動画にのみ使用します。著作権および切り抜きガイドラインの確認は自己責任で行います。{" "}
                  <a href="/terms" className="font-medium text-primary underline-offset-2 hover:underline">
                    利用規約を読む
                  </a>
                </span>
              </label>
              {errors.agreed_terms && (
                <p className="text-red-600 text-sm">{errors.agreed_terms.message}</p>
              )}
            </div>

            {/* 送信ボタン */}
            <button
              type="submit"
              disabled={!agreed || isSubmitting}
              className="group inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-6 py-3.5 text-base font-semibold text-primary-foreground shadow-sm transition hover:opacity-90 focus:outline-none focus:ring-4 focus:ring-primary/30 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {isSubmitting ? "送信中..." : "切り抜きを作る"}
              {!isSubmitting && (
                <ArrowRight aria-hidden="true" className="size-5 transition-transform group-hover:translate-x-0.5" />
              )}
            </button>
          </form>
        </section>

        <p className="mt-6 text-center text-sm text-muted-foreground">
          登録不要 · 無料でお試しいただけます
        </p>
      </div>
    </div>
  );
}
