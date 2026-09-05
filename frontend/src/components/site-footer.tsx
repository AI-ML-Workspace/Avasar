import Link from "next/link";
import Image from "next/image";

export function SiteFooter() {
  return (
    <footer className="relative z-10 border-t border-border/80 bg-card/90 backdrop-blur-md">
      <div className="mx-auto grid max-w-6xl gap-8 px-5 py-12 sm:grid-cols-2 lg:grid-cols-3">
        <div>
          <div className="flex items-center gap-3">
            <div className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-white p-0.5 shadow-xs ring-1 ring-border">
              <Image
                src="/logo.png"
                alt="Avasar Logo"
                width={40}
                height={40}
                className="h-full w-full rounded-full object-contain"
              />
            </div>
            <div>
              <h2 className="text-lg font-bold text-foreground">Avasar</h2>
              <p className="text-xs font-semibold text-muted-foreground">सरकारी योजनाएं, बेहतर भविष्य</p>
            </div>
          </div>
          <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
            Government benefits, in your language. Grounded in verified official sources.
          </p>
        </div>

        <nav className="flex flex-col gap-2 text-sm font-medium text-muted-foreground">
          <Link href="/" className="hover:text-foreground transition">
            Home
          </Link>
          <Link href="/schemes" className="hover:text-foreground transition">
            Browse Schemes
          </Link>
          <Link href="/how-it-works" className="hover:text-foreground transition">
            How it works
          </Link>
          <Link href="/chat" className="hover:text-foreground transition">
            Ask Avasar Assistant
          </Link>
        </nav>

        <p className="text-xs text-muted-foreground leading-relaxed">
          Avasar provides grounded information based on available government scheme records. Please verify important
          eligibility criteria and application forms on official government portals.
        </p>
      </div>
    </footer>
  );
}
