"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { ChatPanel } from "@/components/chat-panel";
import { SiteHeader } from "@/components/site-header";
import { MandalaBackground } from "@/components/ui/mandala-background";
import type { LanguageCode } from "@/data/languages";

function ChatContent() {
  const searchParams = useSearchParams();
  const q = searchParams.get("q") ?? undefined;
  const lang = (searchParams.get("lang") as LanguageCode) ?? undefined;

  return (
    <ChatPanel
      key={`${lang || "default"}-${q || ""}`}
      initialQuestion={q}
      initialLanguage={lang}
    />
  );
}

export default function ChatPage() {
  return (
    <>
      <div className="page-background">
        <MandalaBackground />
      </div>

      <div className="page-content flex min-h-screen flex-col">
        <SiteHeader />
        <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-6 sm:px-6">
          <div className="h-[calc(100vh-9.5rem)]">
            <Suspense
              fallback={
                <div className="flex h-full w-full items-center justify-center rounded-3xl floating-card">
                  <p className="text-sm font-medium text-muted-foreground">Loading assistant…</p>
                </div>
              }
            >
              <ChatContent />
            </Suspense>
          </div>
        </main>
      </div>
    </>
  );
}
