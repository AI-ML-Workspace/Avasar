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

import { useState, useEffect } from "react";

function SchemeCard({ scheme }: { scheme: (typeof schemes)[0] }) {
  const [imgSrc, setImgSrc] = useState(scheme.image || "/logo.png");

  return (
    <Link
      href={`/schemes/${scheme.slug}`}
      className="group flex flex-col overflow-hidden rounded-3xl floating-card transition hover:shadow-lg"
    >
      {/* Scheme Card Image */}
      <div className="relative h-52 w-full overflow-hidden bg-secondary border-b border-black/10">
        <Image
          src={imgSrc}
          alt={scheme.name}
          fill
          unoptimized
          onError={() => setImgSrc("/logo.png")}
          className="object-cover transition duration-300 group-hover:scale-105"
        />
        <span className="absolute top-3 left-3 rounded-full border border-black/20 bg-white/95 px-3 py-1 text-[11px] font-bold text-[#2A1503] backdrop-blur-md shadow-xs">
          {scheme.category}
        </span>
      </div>

      <div className="flex flex-1 flex-col p-5 sm:p-6 bg-white/95">
        <h2 className="text-lg font-bold text-[#2A1503] group-hover:text-primary transition leading-snug">
          {scheme.name}
        </h2>
        <p className="mt-2 flex-1 text-sm text-muted-foreground leading-relaxed line-clamp-3">
          {scheme.summary}
        </p>
        <span className="mt-4 inline-flex items-center text-xs font-bold text-primary group-hover:text-accent transition">
          View scheme details{" "}
          <ArrowRight className="ml-1.5 h-4 w-4 transition group-hover:translate-x-1" />
        </span>
      </div>
    </Link>
  );
}

function SchemesContent() {
  const searchParams = useSearchParams();
  const categoryParam = searchParams.get("category");
  const [allSchemes, setAllSchemes] = useState(schemes);
  const [searchQuery, setSearchQuery] = useState("");

  // Dynamically synchronize with backend API
  useEffect(() => {
    let isMounted = true;
    fetch("/api/schemes")
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (isMounted && data && Array.isArray(data.schemes) && data.schemes.length > 0) {
          setAllSchemes(data.schemes);
        }
      })
      .catch(() => {
        // Gracefully keep preloaded schemes
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const filtered = allSchemes.filter((s) => {
    const matchesCategory = !categoryParam || s.category.toLowerCase() === categoryParam.toLowerCase();
    const query = searchQuery.trim().toLowerCase();
    const matchesSearch =
      !query ||
      s.name.toLowerCase().includes(query) ||
      s.summary.toLowerCase().includes(query) ||
      s.category.toLowerCase().includes(query);
    return matchesCategory && matchesSearch;
  });

  return (
    <>
      {/* Search Input Bar */}
      <div className="mt-6 flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:max-w-md">
          <input
            type="text"
            placeholder="Search schemes by name, keyword, or benefits..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-2xl border border-black/20 bg-white/90 px-4 py-2.5 text-sm text-[#2A1503] placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary shadow-xs"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3 top-2.5 text-xs text-muted-foreground hover:text-black font-bold"
            >
              Clear
            </button>
          )}
        </div>
        <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider self-start sm:self-center">
          Showing {filtered.length} of {allSchemes.length} Schemes
        </span>
      </div>

      {/* Category Filter Pills */}
      <div className="mt-4 flex flex-wrap gap-2">
        <Link
          href="/schemes"
          className={`rounded-full border px-4 py-2 text-xs font-semibold transition ${
            !categoryParam
              ? "border-primary bg-primary text-primary-foreground shadow-xs"
              : "border-border/80 bg-card text-foreground hover:border-accent hover:bg-secondary"
          }`}
        >
          All Categories ({allSchemes.length})
        </Link>
        {categories.map((c) => {
          const count = allSchemes.filter((s) => s.category.toLowerCase() === c.toLowerCase()).length;
          return (
            <Link
              key={c}
              href={`/schemes?category=${encodeURIComponent(c)}`}
              className={`rounded-full border px-4 py-2 text-xs font-semibold transition ${
                categoryParam?.toLowerCase() === c.toLowerCase()
                  ? "border-primary bg-primary text-primary-foreground shadow-xs"
                  : "border-border/80 bg-card text-foreground hover:border-accent hover:bg-secondary"
              }`}
            >
              {c} {count > 0 ? `(${count})` : ""}
            </Link>
          );
        })}
      </div>

      {/* Scheme Cards Grid */}
      <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((s) => (
          <SchemeCard key={s.slug} scheme={s} />
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="mt-12 rounded-3xl floating-card p-8 text-center">
          <p className="text-base font-bold text-[#2A1503]">No matching schemes found.</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Try adjusting your search terms or selecting a different category.
          </p>
          <button
            onClick={() => setSearchQuery("")}
            className="mt-4 inline-flex rounded-xl bg-primary px-4 py-2 text-xs font-bold text-primary-foreground hover:opacity-95 transition"
          >
            Reset Search
          </button>
        </div>
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
