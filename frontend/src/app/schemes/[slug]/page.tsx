import Link from "next/link";
import Image from "next/image";
import { notFound } from "next/navigation";
import { ExternalLink, CheckCircle2, ArrowLeft } from "lucide-react";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import { MandalaBackground } from "@/components/ui/mandala-background";
import { getScheme, schemes } from "@/data/schemes";

type Props = {
  params: Promise<{ slug: string }>;
};

export async function generateStaticParams() {
  return schemes.map((scheme) => ({
    slug: scheme.slug,
  }));
}

export async function generateMetadata({ params }: Props) {
  const { slug } = await params;
  const scheme = getScheme(slug);
  if (!scheme) return { title: "Scheme Not Found — Avasar" };
  return {
    title: `${scheme.name} — Avasar`,
    description: scheme.summary,
  };
}

function Section({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-3xl border border-border/80 bg-card p-6 shadow-soft hover:border-accent/40 transition">
      <h2 className="text-base font-bold text-foreground">{title}</h2>
      <ul className="mt-4 space-y-2.5 text-sm text-foreground/90">
        {items.map((i) => (
          <li key={i} className="flex items-start gap-2.5">
            <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-amber-700 dark:text-amber-400" />
            <span className="leading-relaxed">{i}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default async function SchemeDetailPage({ params }: Props) {
  const { slug } = await params;
  const scheme = getScheme(slug);
  if (!scheme) {
    notFound();
  }

  return (
    <div className="relative flex min-h-screen flex-col bg-background text-foreground overflow-x-hidden">
      <MandalaBackground />

      <div className="relative z-10 flex flex-col min-h-screen">
        <SiteHeader />
        <main className="mx-auto w-full max-w-4xl flex-1 px-5 py-10">
          <Link
            href="/schemes"
            className="inline-flex items-center gap-1.5 text-xs font-bold text-muted-foreground hover:text-foreground transition uppercase tracking-wider mb-4"
          >
            <ArrowLeft className="h-3.5 w-3.5" /> All schemes
          </Link>

          {/* Scheme Banner Image */}
          <div className="relative h-56 sm:h-72 w-full overflow-hidden rounded-3xl mb-6 shadow-soft border border-border/80">
            <Image
              src={scheme.image || "/logo.png"}
              alt={scheme.name}
              fill
              className="object-cover"
              priority
            />
            <span className="absolute top-4 left-4 rounded-full border border-accent/40 bg-card/90 px-3.5 py-1 text-xs font-bold text-foreground backdrop-blur-md shadow-xs">
              {scheme.category}
            </span>
          </div>

          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl leading-tight">
              {scheme.name}
            </h1>
            <p className="mt-3 text-base text-muted-foreground leading-relaxed">{scheme.description}</p>
          </div>

          <div className="mt-8 grid gap-5 sm:grid-cols-2">
            <Section title="👥 Who is eligible?" items={scheme.eligibility} />
            <Section title="💰 Benefits" items={scheme.benefits} />
            <Section title="📄 Required documents" items={scheme.documents} />
            <Section title="📝 How to apply" items={scheme.howToApply} />
            <Section title="📍 Where to apply" items={[scheme.whereToApply]} />
            <Section title="⚠️ Important conditions" items={scheme.conditions} />
          </div>

          <div className="mt-8 flex flex-col gap-4 rounded-3xl border border-accent/40 bg-primary p-6 text-primary-foreground sm:flex-row sm:items-center sm:justify-between shadow-lift">
            <p className="text-sm leading-relaxed">
              Verify eligibility and application details on the official government website.
            </p>
            <a
              href={scheme.source.url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex w-fit items-center gap-2 rounded-xl bg-accent px-5 py-3 text-sm font-bold text-accent-foreground shadow-sm hover:opacity-95 transition shrink-0"
            >
              {scheme.source.label} <ExternalLink className="h-4 w-4" />
            </a>
          </div>

          <div className="mt-6 rounded-3xl border border-border/80 bg-card p-6 shadow-soft">
            <p className="text-sm text-muted-foreground">
              Have a question about this scheme?{" "}
              <Link
                href={`/chat?q=${encodeURIComponent(`Am I eligible for ${scheme.name}?`)}`}
                className="font-bold text-primary hover:text-accent underline underline-offset-3"
              >
                Ask Avasar Assistant
              </Link>
              .
            </p>
          </div>
        </main>
        <SiteFooter />
      </div>
    </div>
  );
}
