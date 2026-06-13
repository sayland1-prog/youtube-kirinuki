"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
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
    <div className="space-y-8">
      {/* ヒーロー */}
      <div className="text-center space-y-3 pt-4">
        <h1 className="text-3xl font-bold leading-tight">
          URLを貼るだけ。<br />
          切り抜きショート、30分で完成。
        </h1>
        <p className="text-gray-600 text-base">
          文字起こし・選定・字幕・投稿文まで全自動。<br />
          切り抜き許可をもらったら、あとはURLだけ。
        </p>
      </div>

      {/* フォームカード */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-5">
        {serverError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800 text-sm">
            {serverError}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
          {/* YouTube URL */}
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">
              YouTube の URL
            </label>
            <input
              {...register("youtube_url")}
              type="url"
              inputMode="url"
              placeholder="https://www.youtube.com/watch?v=..."
              className={`w-full border rounded-lg px-4 py-3 text-base focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${
                errors.youtube_url ? "border-red-500 focus:ring-red-500" : "border-gray-300"
              }`}
            />
            {errors.youtube_url && (
              <p className="text-red-600 text-sm">{errors.youtube_url.message}</p>
            )}
          </div>

          {/* メールアドレス */}
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">
              メールアドレス
            </label>
            <input
              {...register("email")}
              type="email"
              inputMode="email"
              placeholder="you@example.com"
              className={`w-full border rounded-lg px-4 py-3 text-base focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${
                errors.email ? "border-red-500 focus:ring-red-500" : "border-gray-300"
              }`}
            />
            {errors.email && (
              <p className="text-red-600 text-sm">{errors.email.message}</p>
            )}
          </div>

          {/* 利用規約同意 */}
          <div className="space-y-1">
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                {...register("agreed_terms")}
                type="checkbox"
                className="mt-1 w-4 h-4 accent-blue-600 flex-shrink-0"
              />
              <span className="text-sm text-gray-700">
                切り抜き許可のある動画にのみ使用します。著作権および切り抜きガイドラインの確認は自己責任で行います。
                <a href="/terms" className="text-primary underline ml-1">
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
            className={`w-full py-3 px-6 rounded-lg font-medium text-white text-base transition-opacity ${
              !agreed || isSubmitting
                ? "bg-primary opacity-50 cursor-not-allowed"
                : "bg-primary hover:bg-primary-hover"
            }`}
          >
            {isSubmitting ? "送信中..." : "切り抜きを作る →"}
          </button>
        </form>
      </div>

      <p className="text-center text-sm text-gray-500">
        登録不要 · 無料でお試しいただけます
      </p>
    </div>
  );
}
