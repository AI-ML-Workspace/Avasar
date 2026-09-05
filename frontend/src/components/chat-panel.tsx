"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import {
  ArrowUp,
  Copy,
  RotateCcw,
  Square,
  Trash2,
  User,
  ExternalLink,
  BookOpen,
  Sparkles,
  ShieldCheck,
  Check,
} from "lucide-react";
import { toast } from "sonner";
import { languages, suggestedPrompts, type LanguageCode } from "@/data/languages";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { StructuredSchemeResponse } from "@/components/structured-scheme-response";

export type SourceItem = {
  title: string;
  url?: string | null;
  snippet: string;
  score: number;
};

export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceItem[];
};

const newId = () => Math.random().toString(36).slice(2);

export function ChatPanel({
  initialQuestion,
  initialLanguage,
}: {
  initialQuestion?: string;
  initialLanguage?: LanguageCode;
}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [language, setLanguage] = useState<LanguageCode>(initialLanguage || "en");
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const startedRef = useRef(false);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = async (text: string, history: Message[]) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    const userMessage: Message = { id: newId(), role: "user", content: trimmed };
    const next = [...history, userMessage];
    setMessages(next);
    setInput("");
    setLoading(true);

    const controller = new AbortController();
    abortRef.current = controller;
    const assistantId = newId();

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: controller.signal,
        body: JSON.stringify({
          message: trimmed,
          language: language,
          conversation_id: conversationId,
        }),
      });

      if (res.status === 429) {
        throw new Error("Too many requests right now. Please try again in a moment.");
      }
      if (res.status === 402) {
        throw new Error("The assistant is out of credits. Please try again later.");
      }
      if (!res.ok) {
        let errorDetail = "Avasar could not answer just now. Please try again.";
        try {
          const errJson = await res.json();
          if (errJson?.detail) errorDetail = errJson.detail;
        } catch {
          // Ignore JSON parse error
        }
        throw new Error(errorDetail);
      }

      const data = await res.json();
      if (data.conversation_id) {
        setConversationId(data.conversation_id);
      }
      if (data.language && languages.some((l) => l.code === data.language)) {
        setLanguage(data.language as LanguageCode);
      }
      setMessages([
        ...next,
        {
          id: assistantId,
          role: "assistant",
          content: data.answer || "No response received.",
          sources: Array.isArray(data.sources) ? data.sources : [],
        },
      ]);
    } catch (err) {
      if ((err as Error).name === "AbortError") {
        setMessages((prev) => prev.filter((m) => m.content.trim() !== ""));
      } else {
        setMessages((prev) => prev.filter((m) => m.id !== assistantId));
        toast.error((err as Error).message);
      }
    } finally {
      setLoading(false);
      abortRef.current = null;
    }
  };

  useEffect(() => {
    if (initialQuestion && !startedRef.current) {
      startedRef.current = true;
      void send(initialQuestion, []);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialQuestion]);

  const regenerate = () => {
    const lastUser = [...messages].reverse().find((m) => m.role === "user");
    if (!lastUser) return;
    const idx = messages.findIndex((m) => m.id === lastUser.id);
    void send(lastUser.content, messages.slice(0, idx));
  };

  const copyToClipboard = (id: string, content: string) => {
    void navigator.clipboard.writeText(content);
    setCopiedId(id);
    toast.success("Copied to clipboard");
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-3xl border border-border/90 bg-card/95 shadow-lift backdrop-blur-md transition-all">
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border/80 bg-secondary/60 px-5 py-3.5">
        <div className="flex items-center gap-3">
          <div className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-white p-0.5 shadow-md ring-2 ring-accent/30">
            <Image
              src="/logo.png"
              alt="Avasar Assistant"
              width={40}
              height={40}
              className="h-full w-full rounded-full object-contain"
            />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-foreground">Avasar Assistant</h3>
              <span className="inline-flex items-center gap-1 rounded-full border border-accent/40 bg-accent/15 px-2 py-0.5 text-[10px] font-semibold text-foreground">
                <Sparkles className="h-3 w-3 text-accent" /> Verified RAG
              </span>
            </div>
            <p className="text-xs text-muted-foreground">Ask about any Indian government scheme</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Select value={language} onValueChange={(v) => setLanguage(v as LanguageCode)}>
            <SelectTrigger className="h-9 w-[150px] rounded-xl border-border bg-card text-xs font-semibold shadow-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="rounded-xl">
              {languages.map((l) => (
                <SelectItem key={l.code} value={l.code} className="text-xs">
                  <span className="font-semibold">{l.native}</span>{" "}
                  <span className="text-muted-foreground">({l.label})</span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {messages.length > 0 && (
            <Button
              variant="outline"
              size="icon"
              className="h-9 w-9 rounded-xl border-border hover:bg-destructive/10 hover:text-destructive transition"
              aria-label="Clear conversation"
              title="Clear conversation"
              onClick={() => {
                setMessages([]);
                setConversationId(null);
                toast.info("Conversation cleared");
              }}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 space-y-6 overflow-y-auto px-4 py-6 sm:px-6">
        {messages.length === 0 && (
          <div className="mx-auto max-w-xl py-6 text-center">
            <div className="relative mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-white p-1 shadow-md ring-4 ring-accent/20">
              <Image
                src="/logo.png"
                alt="Avasar"
                width={60}
                height={60}
                className="h-full w-full rounded-full object-contain"
              />
            </div>
            <h2 className="text-xl font-bold text-foreground sm:text-2xl">
              Namaste! How can I help you today?
            </h2>
            <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
              Ask in your preferred language — English, हिन्दी, தமிழ், తెలుగు, ಕನ್ನಡ or other Indian languages.
            </p>

            <div className="mt-6 grid gap-2.5 text-left">
              <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider pl-1">
                Suggested Questions
              </p>
              {suggestedPrompts.map((p) => (
                <button
                  key={p}
                  onClick={() => void send(p, messages)}
                  className="group flex items-center justify-between rounded-2xl border border-border/80 bg-secondary/50 px-4 py-3.5 text-sm font-medium text-foreground transition-all hover:border-accent hover:bg-card hover:shadow-soft cursor-pointer"
                >
                  <span>{p}</span>
                  <ArrowUp className="h-4 w-4 text-muted-foreground rotate-45 transition group-hover:text-primary group-hover:translate-x-0.5" />
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m) =>
          m.role === "user" ? (
            <div key={m.id} className="flex justify-end gap-3 items-start">
              <div className="max-w-[85%] rounded-2xl rounded-tr-xs bg-primary px-4 py-3 text-sm font-medium text-primary-foreground shadow-sm">
                <p className="whitespace-pre-wrap leading-relaxed">{m.content}</p>
              </div>
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary text-foreground shadow-xs font-bold text-xs">
                <User className="h-4 w-4" />
              </span>
            </div>
          ) : (
            <div key={m.id} className="group flex gap-3.5 items-start">
              <div className="relative mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white p-0.5 shadow-md ring-2 ring-accent/30">
                <Image
                  src="/logo.png"
                  alt="Avasar Logo"
                  width={36}
                  height={36}
                  className="h-full w-full rounded-full object-contain"
                />
              </div>

              <div className="min-w-0 flex-1 space-y-4">
                <StructuredSchemeResponse content={m.content} />

                {/* Verified Sources & Citations */}
                {m.sources && m.sources.length > 0 && (
                  <div className="rounded-2xl border border-border/80 bg-secondary/50 p-4 shadow-xs">
                    <div className="flex items-center justify-between gap-2 border-b border-border/60 pb-2">
                      <p className="flex items-center gap-1.5 text-xs font-bold text-foreground uppercase tracking-wider">
                        <BookOpen className="h-4 w-4 text-accent" /> Verified Government Sources ({m.sources.length})
                      </p>
                      <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-foreground bg-accent/20 px-2.5 py-0.5 rounded-full border border-accent/40">
                        <ShieldCheck className="h-3 w-3 text-accent" /> Grounded
                      </span>
                    </div>

                    <div className="mt-3 grid gap-2.5">
                      {m.sources.map((s, sIdx) => (
                        <div
                          key={sIdx}
                          className="rounded-xl border border-border/60 bg-card p-3 text-xs shadow-xs transition hover:border-accent/40"
                        >
                          <div className="flex flex-wrap items-center justify-between gap-2">
                            <span className="font-semibold text-foreground">{s.title}</span>
                            {s.url && (s.url.startsWith("http://") || s.url.startsWith("https://")) && (
                              <a
                                href={s.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1 font-semibold text-primary hover:text-accent bg-primary/10 px-2.5 py-1 rounded-lg text-[11px] transition"
                              >
                                Official Portal <ExternalLink className="h-3 w-3" />
                              </a>
                            )}
                          </div>
                          <p className="mt-1.5 line-clamp-2 text-muted-foreground leading-relaxed">
                            {s.snippet}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Copy & Retry Actions */}
                {m.content && !loading && (
                  <div className="flex items-center gap-1.5 pt-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 rounded-lg px-2.5 text-xs text-muted-foreground hover:text-foreground hover:bg-secondary"
                      onClick={() => copyToClipboard(m.id, m.content)}
                    >
                      {copiedId === m.id ? (
                        <>
                          <Check className="mr-1 h-3.5 w-3.5 text-emerald-700" /> Copied
                        </>
                      ) : (
                        <>
                          <Copy className="mr-1 h-3.5 w-3.5" /> Copy
                        </>
                      )}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 rounded-lg px-2.5 text-xs text-muted-foreground hover:text-foreground hover:bg-secondary"
                      onClick={regenerate}
                    >
                      <RotateCcw className="mr-1 h-3.5 w-3.5" /> Retry
                    </Button>
                  </div>
                )}
              </div>
            </div>
          ),
        )}

        {/* Loading Indicator */}
        {loading && (
          <div className="flex items-start gap-3">
            <div className="relative mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white p-0.5 shadow-md ring-2 ring-accent/30 animate-pulse">
              <Image
                src="/logo.png"
                alt="Avasar Loading"
                width={36}
                height={36}
                className="h-full w-full rounded-full object-contain"
              />
            </div>
            <div className="rounded-2xl border border-border/80 bg-card p-4 shadow-xs">
              <div className="flex items-center gap-3">
                <div className="flex space-x-1.5">
                  <span className="h-2 w-2 rounded-full bg-primary animate-bounce [animation-delay:-0.3s]" />
                  <span className="h-2 w-2 rounded-full bg-accent animate-bounce [animation-delay:-0.15s]" />
                  <span className="h-2 w-2 rounded-full bg-amber-700 animate-bounce" />
                </div>
                <p className="text-xs font-medium text-muted-foreground">
                  Searching verified government scheme records…
                </p>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input Footer Area */}
      <div className="border-t border-border/80 bg-secondary/40 p-4 sm:p-5 backdrop-blur-md">
        <div className="relative flex items-end gap-2 rounded-2xl border border-border/80 bg-card p-2 shadow-xs focus-within:border-accent focus-within:ring-2 focus-within:ring-accent/20 transition-all">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                void send(input, messages);
              }
            }}
            placeholder="Ask about scheme eligibility, financial benefits, required documents, or steps to apply…"
            rows={2}
            className="min-h-[52px] flex-1 resize-none border-none bg-transparent px-3 py-2 text-sm font-medium text-foreground outline-none focus-visible:ring-0 placeholder:text-muted-foreground"
          />

          <div className="flex items-center gap-1.5 pb-1 pr-1">
            {loading ? (
              <Button
                size="icon"
                variant="secondary"
                className="h-10 w-10 rounded-xl bg-destructive/10 text-destructive hover:bg-destructive/20 transition"
                aria-label="Stop generation"
                title="Stop generation"
                onClick={() => abortRef.current?.abort()}
              >
                <Square className="h-4 w-4 fill-current" />
              </Button>
            ) : (
              <Button
                size="icon"
                className="h-10 w-10 rounded-xl bg-primary text-primary-foreground font-bold shadow-soft hover:bg-primary/90 disabled:opacity-40 transition-all cursor-pointer"
                aria-label="Send message"
                disabled={!input.trim()}
                onClick={() => void send(input, messages)}
              >
                <ArrowUp className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>

        <div className="mt-2.5 flex items-center justify-between px-1 text-[11px] text-muted-foreground">
          <span className="hidden sm:inline">Press <strong>Enter ↵</strong> to send, <strong>Shift + Enter</strong> for line break</span>
          <span className="flex items-center gap-1 font-medium text-muted-foreground ml-auto">
            <ShieldCheck className="h-3.5 w-3.5 text-accent" /> Grounded in verified govt sources
          </span>
        </div>
      </div>
    </div>
  );
}
