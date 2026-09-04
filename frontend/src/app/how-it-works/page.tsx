import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";

export const metadata = {
  title: "How Avasar works — Government schemes made simple",
  description:
    "Learn how Avasar helps Indian citizens find government schemes: ask in your language, understand eligibility and apply at the official source.",
};

const steps = [
  {
    title: "1. Ask in your language",
    body: "Type your question in English, Hindi, Tamil, Telugu or Kannada. Share details like your age, state, occupation or income for more relevant answers.",
  },
  {
    title: "2. Get a clear explanation",
    body: "Avasar breaks each scheme into eligibility, benefits, required documents, how to apply, where to apply and important conditions.",
  },
  {
    title: "3. Apply at the official source",
    body: "Every answer links to the official government portal or tells you which office to visit, so you can complete your application confidently.",
  },
];

export default function HowItWorksPage() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-3xl flex-1 px-5 py-14">
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">How Avasar works</h1>
        <p className="mt-3 text-muted-foreground">
          Avasar is a citizen-first assistant that makes government schemes easier to discover and
          understand — without the jargon of a traditional portal.
        </p>
        <div className="mt-8 space-y-4">
          {steps.map((s) => (
            <div key={s.title} className="rounded-3xl border border-border bg-card p-6 shadow-soft">
              <h2 className="text-lg font-semibold text-foreground">{s.title}</h2>
              <p className="mt-2 text-sm text-muted-foreground">{s.body}</p>
            </div>
          ))}
        </div>
        <div className="mt-8 rounded-3xl bg-secondary p-6 text-sm text-secondary-foreground shadow-sm">
          Avasar provides information based on available government sources. Please verify important
          eligibility and application details on the official website.
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
