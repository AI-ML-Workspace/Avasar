"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, ShieldCheck, Sparkles, Search } from "lucide-react";
import { MandalaBackground } from "@/components/ui/mandala-background";
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
    <>
      <div className="page-background">
        <MandalaBackground />
      </div>

      <div className="page-content min-h-screen">
        <section className="relative min-h-[85vh]">
          <SiteHeader transparent={false} />

          <div className="relative mx-auto max-w-4xl px-5 pt-16 sm:pt-24 text-center">
            <span className="inline-flex items-center gap-2 rounded-full border border-black/80 bg-secondary/80 px-4 py-1.5 text-xs font-semibold text-foreground shadow-xs backdrop-blur-md">
              <Sparkles className="h-3.5 w-3.5 text-accent" /> Multilingual AI Assistant for Indian Government Schemes
            </span>

            <h1 className="mt-6 text-4xl font-extrabold tracking-tight text-[#2A1503] sm:text-6xl leading-[1.15]">
              Government benefits, <br className="hidden sm:inline" />
              in your language.
            </h1>

            {/* Search Card Container - Floating Cream Card */}
            <div className="relative mx-auto mt-10 max-w-2xl rounded-3xl floating-card p-3 shadow-lift backdrop-blur-md">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                <Select value={language} onValueChange={(v) => setLanguage(v as LanguageCode)}>
                  <SelectTrigger className="h-12 w-full rounded-2xl border border-black/70 bg-secondary/70 text-xs font-semibold text-foreground sm:w-[150px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="rounded-xl border border-black">
                    {languages.map((l) => (
                      <SelectItem key={l.code} value={l.code} className="text-xs">
                        <span className="font-semibold">{l.native}</span>{" "}
                        <span className="text-muted-foreground">({l.label})</span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <div className="relative flex-1">
                  <input
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && ask(question)}
                    placeholder="Ask e.g. What schemes can I apply for as a student?"
                    className="h-12 w-full rounded-2xl bg-transparent px-4 pr-10 text-sm font-medium text-foreground outline-none placeholder:text-muted-foreground"
                  />
                  <Search className="absolute right-3.5 top-3.5 h-5 w-5 text-muted-foreground/60 pointer-events-none" />
                </div>

                <Button
                  size="lg"
                  className="h-12 rounded-2xl bg-primary text-primary-foreground font-semibold shadow-soft hover:bg-primary/90 border border-black cursor-pointer"
                  onClick={() => ask(question)}
                >
                  Ask Avasar <ArrowRight className="ml-1.5 h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Suggested Prompts */}
            <div className="mx-auto mt-6 flex max-w-3xl flex-wrap justify-center gap-2">
              {suggestedPrompts.map((p) => (
                <button
                  key={p}
                  onClick={() => ask(p)}
                  className="rounded-full border border-black/80 bg-card/95 px-4 py-2 text-xs font-semibold text-[#2A1503] shadow-xs transition hover:bg-secondary cursor-pointer"
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          {/* Circular Showcase Gallery */}
          <div className="relative mt-12 h-[28rem] w-full pb-6">
            <CircularGalleryClient items={galleryItems} />
          </div>
        </section>

        {/* Clean Value Pillars */}
        <section className="relative mx-auto max-w-6xl px-5 py-14">
          <div className="grid gap-6 sm:grid-cols-3">
            {[
              {
                title: "Ask in your language",
                body: "English, हिन्दी, தமிழ், తెలుగు and ಕನ್ನಡ — ask naturally without jargon.",
              },
              {
                title: "Understand clearly",
                body: "Eligibility, benefits, documents, and steps in clean structured cards.",
              },
              {
                title: "Official Government Portals",
                body: "Every answer links directly to verified government portals.",
              },
            ].map((c) => (
              <div
                key={c.title}
                className="rounded-3xl floating-card p-6"
              >
                <h2 className="text-lg font-bold text-[#2A1503]">{c.title}</h2>
                <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{c.body}</p>
              </div>
            ))}
          </div>

          {/* Verified Banner */}
          <div className="mt-10 flex flex-col items-start gap-4 rounded-3xl border border-black bg-primary p-7 text-primary-foreground sm:flex-row sm:items-center sm:justify-between shadow-lift">
            <div className="flex items-center gap-3">
              <ShieldCheck className="h-6 w-6 text-accent shrink-0" />
              <p className="text-sm font-medium">
                Grounded strictly in verified Indian government records.
              </p>
            </div>
            <Link
              href="/schemes"
              className="rounded-xl bg-accent border border-black px-5 py-2.5 text-xs font-bold text-accent-foreground shadow-xs hover:opacity-95 transition shrink-0"
            >
              Browse All Schemes
            </Link>
          </div>
        </section>

        <SiteFooter />
      </div>
    </>
  );
}
