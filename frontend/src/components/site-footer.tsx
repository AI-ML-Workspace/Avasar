import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="border-t border-border bg-card">
      <div className="mx-auto grid max-w-6xl gap-8 px-5 py-12 sm:grid-cols-2 lg:grid-cols-3">
        <div>
          <h2 className="text-lg font-semibold text-foreground">Avasar</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Government benefits, in your language.
          </p>
        </div>
        <nav className="flex flex-col gap-2 text-sm text-muted-foreground">
          <Link href="/" className="hover:text-foreground">
            Home
          </Link>
          <Link href="/schemes" className="hover:text-foreground">
            Schemes
          </Link>
          <Link href="/how-it-works" className="hover:text-foreground">
            How it works
          </Link>
          <Link href="/chat" className="hover:text-foreground">
            Ask Avasar
          </Link>
        </nav>
        <p className="text-sm text-muted-foreground">
          Avasar provides information based on available government sources. Please verify important
          eligibility and application details on the official website.
        </p>
      </div>
    </footer>
  );
}
