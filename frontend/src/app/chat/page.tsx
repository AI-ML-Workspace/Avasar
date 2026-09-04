"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { ChatPanel } from "@/components/chat-panel";
import { SiteHeader } from "@/components/site-header";
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
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-3xl flex-1 px-5 py-6">
        <div className="h-[calc(100vh-9rem)]">
          <Suspense
            fallback={
              <div className="flex h-full w-full items-center justify-center rounded-3xl border border-border bg-card">
                <p className="text-sm text-muted-foreground">Loading assistant…</p>
              </div>
            }
          >
            <ChatContent />
          </Suspense>
        </div>
      </main>
    </div>
  );
}
