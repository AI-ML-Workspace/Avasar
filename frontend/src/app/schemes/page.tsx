"use client";

import { Suspense } from "react";
import Link from "next/link";
import Image from "next/image";
import { useSearchParams } from "next/navigation";
import { ArrowRight, Sparkles } from "lucide-react";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import { MandalaBackground } from "@/components/ui/mandala-background";
import { categories, schemes } from "@/data/schemes";

function SchemesContent() {
  const searchParams = useSearchParams();
  const category = searchParams.get("category");
  const filtered = category ? schemes.filter((s) => s.category === category) : schemes;

  return (
    <>
      <div className="mt-6 flex flex-wrap gap-2">
        <Link
          href="/schemes"
          className={`rounded-full border px-4 py-2 text-xs font-semibold transition ${
            !category
              ? "border-primary bg-primary text-primary-foreground shadow-xs"
              : "border-border/80 bg-card text-foreground hover:border-accent hover:bg-secondary"
          }`}
        >
          All Categories
        </Link>
        {categories.map((c) => (
          <Link
            key={c}
            href={`/schemes?category=${encodeURIComponent(c)}`}
            className={`rounded-full border px-4 py-2 text-xs font-semibold transition ${
              category === c
                ? "border-primary bg-primary text-primary-foreground shadow-xs"
                : "border-border/80 bg-card text-foreground hover:border-accent hover:bg-secondary"
            }`}
          >
            {c}
          </Link>
        ))}
      </div>

      <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((s) => (
          <Link
            key={s.slug}
            href={`/schemes/${s.slug}`}
            className="group flex flex-col overflow-hidden rounded-3xl floating-card transition"
          >
            {/* Scheme Card Image */}
            <div className="relative h-56 w-full overflow-hidden bg-secondary border-b border-black/10">
              <Image
                src={s.image || "/logo.png"}
                alt={s.name}
                fill
                className="object-cover transition duration-300 group-hover:scale-105"
              />
              <span className="absolute top-3 left-3 rounded-full border border-black/20 bg-white/95 px-3 py-1 text-[11px] font-bold text-[#2A1503] backdrop-blur-md shadow-xs">
                {s.category}
              </span>
            </div>

            <div className="flex flex-1 flex-col p-5 sm:p-6 bg-white/95">
              <h2 className="text-lg font-bold text-[#2A1503] group-hover:text-primary transition leading-snug">
                {s.name}
              </h2>
              <p className="mt-2 flex-1 text-sm text-muted-foreground leading-relaxed">
                {s.summary}
              </p>
              <span className="mt-4 inline-flex items-center text-xs font-bold text-primary group-hover:text-accent transition">
                View scheme details{" "}
                <ArrowRight className="ml-1.5 h-4 w-4 transition group-hover:translate-x-1" />
              </span>
            </div>
          </Link>
        ))}
      </div>

      {filtered.length === 0 && (
        <p className="mt-10 text-muted-foreground">No schemes listed in this category yet.</p>
      )}
    </>
  );
}

export default function SchemesPage() {
  return (
    <>
      <div className="page-background">
        <MandalaBackground />
      </div>

      <div className="page-content flex min-h-screen flex-col">
        <SiteHeader />
        <main className="mx-auto w-full max-w-6xl flex-1 px-5 py-12">
          <div className="flex items-center gap-2 text-xs font-bold text-accent uppercase tracking-wider">
            <Sparkles className="h-4 w-4" /> Official Scheme Directory
          </div>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight text-[#2A1503] sm:text-4xl">
            Explore government schemes
          </h1>
          <p className="mt-2 text-muted-foreground leading-relaxed">
            Discover verified Indian welfare schemes by category to check eligibility and benefits.
          </p>

          <Suspense fallback={<div className="mt-8 h-48 animate-pulse rounded-3xl floating-card" />}>
            <SchemesContent />
          </Suspense>
        </main>
        <SiteFooter />
      </div>
    </>
  );
}
