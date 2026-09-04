import Link from "next/link";
import { Sun } from "lucide-react";

export function SiteHeader({ transparent = false }: { transparent?: boolean }) {
  return (
    <header
      className={
        transparent
          ? "absolute inset-x-0 top-0 z-30"
          : "sticky top-0 z-30 border-b border-border bg-background/85 backdrop-blur"
      }
    >
      <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4">
        <Link href="/" className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-soft">
            <Sun className="h-5 w-5 text-accent" />
          </span>
          <span
            className={
              transparent
                ? "text-lg font-semibold tracking-tight text-primary-foreground"
                : "text-lg font-semibold tracking-tight text-foreground"
            }
          >
            Avasar
          </span>
        </Link>
        <nav
          className={`flex items-center gap-1 text-sm font-medium ${
            transparent ? "text-primary-foreground" : "text-muted-foreground"
          }`}
        >
          <Link href="/schemes" className="rounded-lg px-3 py-2 hover:bg-accent/20">
            Schemes
          </Link>
          <Link href="/how-it-works" className="rounded-lg px-3 py-2 hover:bg-accent/20">
            How it works
          </Link>
          <Link
            href="/chat"
            className="rounded-lg bg-accent px-4 py-2 text-accent-foreground shadow-soft hover:opacity-90"
          >
            Ask Avasar
          </Link>
        </nav>
      </div>
    </header>
  );
}
