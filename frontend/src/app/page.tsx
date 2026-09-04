"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, ShieldCheck, Sparkle } from "lucide-react";
import { CloudShader } from "@/components/ui/cloud-shader";
import { CircularGalleryClient } from "@/components/circular-gallery-client";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import { galleryItems } from "@/data/gallery-items";
import { languages, suggestedPrompts, type LanguageCode } from "@/data/languages";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function HomePage() {
  const router = useRouter();
  const [question, setQuestion] = useState("");
  const [language, setLanguage] = useState<LanguageCode>("en");

  const ask = (q: string) => {
    const text = q.trim();
    if (!text) return;
    router.push(`/chat?q=${encodeURIComponent(text)}&lang=${encodeURIComponent(language)}`);
  };

  return (
    <div className="min-h-screen bg-background">
      <section className="relative min-h-[92vh]">
        <div className="absolute inset-0">
          <CloudShader className="h-full w-full" speed={0.9} count={6} />
        </div>
        <div className="absolute inset-0 bg-gradient-to-b from-primary/25 via-transparent to-background" />

        <SiteHeader transparent />

        <div className="relative z-10 mx-auto max-w-4xl px-5 pt-28 text-center">
          <span className="inline-flex items-center gap-2 rounded-full bg-primary/85 px-4 py-1.5 text-xs font-medium text-primary-foreground shadow-sm">
            <Sparkle className="h-3.5 w-3.5 text-accent" /> AI assistant for Indian government
            schemes
          </span>
          <h1 className="mt-5 text-4xl font-semibold tracking-tight text-primary-foreground drop-shadow-md sm:text-6xl">
            Government benefits, in your language.
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-base text-primary-foreground/90 drop-shadow sm:text-lg">
            Ask a question the way you would ask a friend. Avasar explains which schemes may fit
            you, what you are eligible for, the documents you need and exactly where to apply.
          </p>

          <div className="glass-panel mx-auto mt-8 max-w-2xl rounded-3xl p-3">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
              <Select value={language} onValueChange={(v) => setLanguage(v as LanguageCode)}>
                <SelectTrigger className="h-12 w-full rounded-2xl border-none bg-secondary sm:w-[140px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {languages.map((l) => (
                    <SelectItem key={l.code} value={l.code}>
                      {l.native}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && ask(question)}
                placeholder="What schemes can I apply for as a student?"
                className="h-12 flex-1 rounded-2xl bg-transparent px-4 text-base text-foreground outline-none placeholder:text-muted-foreground"
              />
              <Button size="lg" className="h-12 rounded-2xl" onClick={() => ask(question)}>
                Ask Avasar <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="mx-auto mt-4 flex max-w-3xl flex-wrap justify-center gap-2">
            {suggestedPrompts.map((p) => (
              <button
                key={p}
                onClick={() => ask(p)}
                className="rounded-full bg-card/85 px-4 py-2 text-sm text-foreground shadow-soft backdrop-blur transition hover:bg-card cursor-pointer"
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        <div className="relative z-10 mt-8 h-[32rem] w-full pb-6">
          <CircularGalleryClient items={galleryItems} />
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 py-16">
        <div className="grid gap-6 sm:grid-cols-3">
          {[
            {
              title: "Ask in your language",
              body: "English, हिन्दी, தமிழ், తెలుగు and ಕನ್ನಡ — type naturally, no forms or jargon.",
            },
            {
              title: "Understand clearly",
              body: "Eligibility, benefits, documents and steps laid out simply, not as walls of text.",
            },
            {
              title: "Go to the right place",
              body: "Every answer points to the official government portal or office to apply.",
            },
          ].map((c) => (
            <div key={c.title} className="rounded-3xl border border-border bg-card p-6 shadow-soft">
              <h2 className="text-lg font-semibold text-foreground">{c.title}</h2>
              <p className="mt-2 text-sm text-muted-foreground">{c.body}</p>
            </div>
          ))}
        </div>

        <div className="mt-10 flex flex-col items-start gap-4 rounded-3xl bg-primary p-8 text-primary-foreground sm:flex-row sm:items-center sm:justify-between shadow-soft">
          <div className="flex items-start gap-3">
            <ShieldCheck className="mt-0.5 h-6 w-6 text-accent shrink-0" />
            <p className="max-w-2xl text-sm">
              Avasar provides information based on available government sources. Please verify
              important eligibility and application details on the official website.
            </p>
          </div>
          <Link
            href="/schemes"
            className="rounded-xl bg-accent px-5 py-3 text-sm font-medium text-accent-foreground shadow hover:opacity-95 transition"
          >
            Browse schemes
          </Link>
        </div>
      </section>

      <SiteFooter />
    </div>
  );
}
