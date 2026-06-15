import { Scissors, FileText, Captions, Send } from "lucide-react"
import { KirinukiForm } from "@/components/kirinuki-form"

const steps = [
  { icon: FileText, label: "文字起こし" },
  { icon: Scissors, label: "選定" },
  { icon: Captions, label: "字幕" },
  { icon: Send, label: "投稿文" },
]

export default function Page() {
  return (
    <main className="min-h-screen">
      <header className="mx-auto flex max-w-3xl items-center gap-2 px-6 py-6">
        <span className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Scissors aria-hidden="true" className="size-4" />
        </span>
        <span className="text-lg font-semibold tracking-tight text-foreground">切り抜きpro</span>
      </header>

      <div className="mx-auto max-w-3xl px-6 pb-20 pt-8 sm:pt-14">
        <section className="flex flex-col items-start gap-6">
          <span className="inline-flex items-center rounded-full border border-border bg-secondary/60 px-3 py-1 text-xs font-medium text-muted-foreground">
            登録不要・無料でお試しいただけます
          </span>

          <h1 className="text-balance text-4xl font-bold leading-tight tracking-tight text-foreground sm:text-5xl">
            URLを貼るだけで切り抜きショートが<span className="text-primary">30分</span>で完成
          </h1>

          <div className="flex flex-col gap-1 text-pretty text-base leading-relaxed text-muted-foreground sm:text-lg">
            <p>文字起こし・選定・字幕・投稿文まで全自動。</p>
            <p>切り抜き許可をもらったら、あとはURLだけ。</p>
          </div>

          <ul className="flex flex-wrap gap-2 pt-1">
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
          <KirinukiForm />
        </section>

        <p className="mt-6 text-center text-sm text-muted-foreground">
          登録不要・無料でお試しいただけます
        </p>
      </div>
    </main>
  )
}
