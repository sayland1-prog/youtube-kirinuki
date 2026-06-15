"use client"

import type React from "react"
import { useState } from "react"
import { ArrowRight, Link, Mail } from "lucide-react"

export function KirinukiForm() {
  const [agreed, setAgreed] = useState(false)

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
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
            id="youtube-url"
            name="youtube-url"
            type="url"
            inputMode="url"
            placeholder="https://www.youtube.com/watch?v=..."
            className="w-full rounded-xl border border-border bg-background py-3 pl-11 pr-4 text-base text-foreground placeholder:text-muted-foreground transition focus:border-primary focus:outline-none focus:ring-4 focus:ring-primary/15"
          />
        </div>
      </div>

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
            id="email"
            name="email"
            type="email"
            inputMode="email"
            placeholder="you@example.com"
            className="w-full rounded-xl border border-border bg-background py-3 pl-11 pr-4 text-base text-foreground placeholder:text-muted-foreground transition focus:border-primary focus:outline-none focus:ring-4 focus:ring-primary/15"
          />
        </div>
      </div>

      <label
        htmlFor="agree"
        className="flex cursor-pointer items-start gap-3 rounded-xl bg-secondary/60 p-4 text-sm leading-relaxed text-muted-foreground"
      >
        <input
          id="agree"
          name="agree"
          type="checkbox"
          checked={agreed}
          onChange={(e) => setAgreed(e.target.checked)}
          className="mt-0.5 size-5 shrink-0 cursor-pointer rounded border-border accent-primary"
        />
        <span>
          切り抜き許可のある動画にのみ使用します。著作権および切り抜きガイドラインの確認は自己責任で行います。{" "}
          <a
            href="#"
            className="font-medium text-primary underline-offset-2 hover:underline"
          >
            利用規約を読む
          </a>
        </span>
      </label>

      <button
        type="submit"
        disabled={!agreed}
        className="group inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-6 py-3.5 text-base font-semibold text-primary-foreground shadow-sm transition hover:opacity-90 focus:outline-none focus:ring-4 focus:ring-primary/30 disabled:cursor-not-allowed disabled:opacity-40"
      >
        切り抜きを作る
        <ArrowRight aria-hidden="true" className="size-5 transition-transform group-hover:translate-x-0.5" />
      </button>
    </form>
  )
}
