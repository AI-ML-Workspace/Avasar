import Link from "next/link";
import { notFound } from "next/navigation";
import { ExternalLink } from "lucide-react";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
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
    <div className="rounded-3xl border border-border bg-card p-6 shadow-soft">
      <h2 className="text-base font-semibold text-foreground">{title}</h2>
      <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
        {items.map((i) => (
          <li key={i} className="flex gap-2">
            <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
            <span>{i}</span>
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
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-4xl flex-1 px-5 py-12">
        <Link href="/schemes" className="text-sm text-muted-foreground hover:text-foreground">
          ← All schemes
        </Link>
        <span className="mt-4 block w-fit rounded-full bg-accent/25 px-3 py-1 text-xs font-medium text-foreground">
          {scheme.category}
        </span>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-foreground">
          {scheme.name}
        </h1>
        <p className="mt-3 text-muted-foreground">{scheme.description}</p>

        <div className="mt-8 grid gap-5 sm:grid-cols-2">
          <Section title="👥 Who is eligible?" items={scheme.eligibility} />
          <Section title="💰 Benefits" items={scheme.benefits} />
          <Section title="📄 Required documents" items={scheme.documents} />
          <Section title="📝 How to apply" items={scheme.howToApply} />
          <Section title="📍 Where to apply" items={[scheme.whereToApply]} />
          <Section title="⚠️ Important conditions" items={scheme.conditions} />
        </div>

        <div className="mt-6 flex flex-col gap-4 rounded-3xl bg-primary p-6 text-primary-foreground sm:flex-row sm:items-center sm:justify-between shadow-soft">
          <p className="text-sm">
            Verify eligibility and application details on the official government website.
          </p>
          <a
            href={scheme.source.url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex w-fit items-center gap-2 rounded-xl bg-accent px-5 py-3 text-sm font-medium text-accent-foreground shadow hover:opacity-95 transition"
          >
            {scheme.source.label} <ExternalLink className="h-4 w-4" />
          </a>
        </div>

        <div className="mt-6 rounded-3xl border border-border bg-card p-6 shadow-soft">
          <p className="text-sm text-muted-foreground">
            Have a question about this scheme?{" "}
            <Link
              href={`/chat?q=${encodeURIComponent(`Am I eligible for ${scheme.name}?`)}`}
              className="font-medium text-primary hover:underline"
            >
              Ask Avasar
            </Link>
            .
          </p>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
