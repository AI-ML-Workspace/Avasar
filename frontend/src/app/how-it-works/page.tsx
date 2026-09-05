import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import { MandalaBackground } from "@/components/ui/mandala-background";
import { Sparkles, ShieldCheck } from "lucide-react";

export const metadata = {
  title: "How Avasar works — Government schemes made simple",
  description:
    "Learn how Avasar helps Indian citizens find government schemes: ask in your language, understand eligibility and apply at the official source.",
};

const steps = [
  {
    title: "1. Ask in your language",
    body: "Type your question in English, Hindi, Tamil, Telugu, Kannada or other Indian languages. Share details like your age, occupation or income for tailored results.",
  },
  {
    title: "2. Get a clear structured explanation",
    body: "Avasar organizes each scheme systematically into eligibility, benefits, required documents, how to apply, where to apply, and important conditions.",
  },
  {
    title: "3. Apply at official government sources",
    body: "Every response links directly to verified government portals or tells you which district office to visit, so you can apply with complete confidence.",
  },
];

export default function HowItWorksPage() {
  return (
    <>
      <div className="page-background">
        <MandalaBackground />
      </div>

      <div className="page-content flex min-h-screen flex-col">
        <SiteHeader />
        <main className="mx-auto w-full max-w-3xl flex-1 px-5 py-12">
          <div className="flex items-center gap-2 text-xs font-bold text-accent uppercase tracking-wider">
            <Sparkles className="h-4 w-4" /> Simple & Transparent
          </div>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight text-[#2A1503] sm:text-4xl">
            How Avasar works
          </h1>
          <p className="mt-3 text-base text-muted-foreground leading-relaxed">
            Avasar is a citizen-first assistant that makes Indian government schemes easy to discover and
            understand — grounded exclusively in verified official records.
          </p>

          <div className="mt-8 space-y-4">
            {steps.map((s) => (
              <div
                key={s.title}
                className="rounded-3xl floating-card p-6"
              >
                <h2 className="text-lg font-bold text-[#2A1503]">{s.title}</h2>
                <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{s.body}</p>
              </div>
            ))}
          </div>

          <div className="mt-8 flex items-start gap-3 rounded-3xl border border-black/80 bg-secondary/90 p-6 text-sm text-[#2A1503] shadow-xs backdrop-blur-md">
            <ShieldCheck className="mt-0.5 h-5 w-5 text-accent shrink-0" />
            <p className="leading-relaxed">
              Avasar provides information based on verified government sources. Please double-check important
              eligibility and application requirements on the official portal before applying.
            </p>
          </div>
        </main>
        <SiteFooter />
      </div>
    </>
  );
}
