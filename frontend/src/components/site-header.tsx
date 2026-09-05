import Link from "next/link";
import Image from "next/image";

export function SiteHeader({ transparent = false }: { transparent?: boolean }) {
  return (
    <header
      className={
        transparent
          ? "absolute inset-x-0 top-0 z-30"
          : "sticky top-0 z-30 border-b border-black/80 bg-background/80 backdrop-blur-md"
      }
    >
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6">
        <Link href="/" className="flex items-center gap-3 group transition">
          <div className="relative flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-white p-0.5 shadow-md ring-2 ring-black/20 transition group-hover:scale-105">
            <Image
              src="/logo.png"
              alt="Avasar Logo"
              width={44}
              height={44}
              className="h-full w-full rounded-full object-contain"
              priority
            />
          </div>
          <div className="flex flex-col">
            <span
              className={
                transparent
                  ? "text-xl font-bold tracking-tight text-primary-foreground drop-shadow-sm"
                  : "text-xl font-bold tracking-tight text-foreground"
              }
            >
              Avasar
            </span>
            <span
              className={
                transparent
                  ? "text-[10px] font-medium tracking-wide text-primary-foreground/80 uppercase"
                  : "text-[10px] font-medium tracking-wide text-muted-foreground uppercase"
              }
            >
              Govt Schemes Assistant
            </span>
          </div>
        </Link>

        <nav
          className={`flex items-center gap-1.5 text-sm font-medium ${
            transparent ? "text-primary-foreground" : "text-foreground"
          }`}
        >
          <Link
            href="/schemes"
            className="rounded-xl px-3.5 py-2 hover:bg-secondary/70 transition"
          >
            Schemes
          </Link>
          <Link
            href="/how-it-works"
            className="rounded-xl px-3.5 py-2 hover:bg-secondary/70 transition"
          >
            How it works
          </Link>
          <Link
            href="/chat"
            className="ml-1 rounded-xl bg-primary px-4 py-2 text-primary-foreground font-semibold shadow-soft hover:bg-primary/90 border border-black transition"
          >
            Ask Avasar
          </Link>
        </nav>
      </div>
    </header>
  );
}
