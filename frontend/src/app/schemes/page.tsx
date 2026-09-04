"use client";

import { Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { ArrowRight } from "lucide-react";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
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
          className={`rounded-full border px-4 py-2 text-sm transition ${
            !category
              ? "border-primary bg-primary text-primary-foreground"
              : "border-border bg-card text-foreground hover:border-accent"
          }`}
        >
          All
        </Link>
        {categories.map((c) => (
          <Link
            key={c}
            href={`/schemes?category=${encodeURIComponent(c)}`}
            className={`rounded-full border px-4 py-2 text-sm transition ${
              category === c
                ? "border-primary bg-primary text-primary-foreground"
                : "border-border bg-card text-foreground hover:border-accent"
            }`}
          >
            {c}
          </Link>
        ))}
      </div>

      <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((s) => (
          <Link
            key={s.slug}
            href={`/schemes/${s.slug}`}
            className="group flex flex-col rounded-3xl border border-border bg-card p-6 shadow-soft transition hover:-translate-y-0.5 hover:shadow-lift"
          >
            <span className="w-fit rounded-full bg-accent/25 px-3 py-1 text-xs font-medium text-foreground">
              {s.category}
            </span>
            <h2 className="mt-3 text-lg font-semibold text-foreground">{s.name}</h2>
            <p className="mt-2 flex-1 text-sm text-muted-foreground">{s.summary}</p>
            <span className="mt-4 inline-flex items-center text-sm font-medium text-primary">
              View details{" "}
              <ArrowRight className="ml-1 h-4 w-4 transition group-hover:translate-x-1" />
            </span>
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
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-6xl flex-1 px-5 py-12">
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">
          Explore government schemes
        </h1>
        <p className="mt-2 text-muted-foreground">
          Pick a category to see schemes that may be relevant to you.
        </p>

        <Suspense fallback={<div className="mt-8 h-48 animate-pulse rounded-3xl bg-card" />}>
          <SchemesContent />
        </Suspense>
      </main>
      <SiteFooter />
    </div>
  );
}
