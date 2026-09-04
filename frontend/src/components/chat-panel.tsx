"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  ArrowUp,
  Copy,
  RotateCcw,
  Square,
  Trash2,
  User,
  Sun,
  ExternalLink,
  BookOpen,
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

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-3xl border border-border bg-card shadow-lift">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-5 py-3">
        <div className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <Sun className="h-4 w-4 text-accent" />
          </span>
          <div>
            <p className="text-sm font-semibold text-foreground">Avasar assistant</p>
            <p className="text-xs text-muted-foreground">Ask about any government scheme</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Select value={language} onValueChange={(v) => setLanguage(v as LanguageCode)}>
            <SelectTrigger className="h-9 w-[140px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {languages.map((l) => (
                <SelectItem key={l.code} value={l.code}>
                  {l.native}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            variant="ghost"
            size="icon"
            aria-label="Clear conversation"
            onClick={() => {
              setMessages([]);
              setConversationId(null);
            }}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="flex-1 space-y-5 overflow-y-auto px-5 py-6">
        {messages.length === 0 && (
          <div className="mx-auto max-w-lg text-center">
            <p className="text-base font-medium text-foreground">
              Namaste! What would you like help with?
            </p>
            <p className="mt-1 text-sm text-muted-foreground">
              Ask in any language — English, हिन्दी, தமிழ், తెలుగు, ಕನ್ನಡ or other Indian languages.
            </p>
            <div className="mt-5 grid gap-2 text-left">
              {suggestedPrompts.map((p) => (
                <button
                  key={p}
                  onClick={() => void send(p, messages)}
                  className="rounded-xl border border-border bg-secondary/60 px-4 py-3 text-sm text-secondary-foreground transition hover:border-accent hover:bg-secondary cursor-pointer"
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m) =>
          m.role === "user" ? (
            <div key={m.id} className="flex justify-end gap-3">
              <div className="max-w-[80%] rounded-2xl rounded-br-md bg-primary px-4 py-3 text-sm text-primary-foreground">
                {m.content}
              </div>
              <span className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-secondary">
                <User className="h-4 w-4 text-secondary-foreground" />
              </span>
            </div>
          ) : (
            <div key={m.id} className="group flex gap-3">
              <span className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary">
                <Sun className="h-4 w-4 text-accent" />
              </span>
              <div className="min-w-0 flex-1">
                <div className="prose prose-sm max-w-none text-foreground prose-headings:text-foreground prose-strong:text-foreground prose-a:text-primary">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
                </div>

                {m.sources && m.sources.length > 0 && (
                  <div className="mt-4 rounded-2xl border border-border/80 bg-secondary/40 p-3.5">
                    <p className="flex items-center gap-1.5 text-xs font-semibold text-foreground">
                      <BookOpen className="h-3.5 w-3.5 text-accent" /> Verified Sources & Citations
                    </p>
                    <div className="mt-2 space-y-2">
                      {m.sources.map((s, sIdx) => (
                        <div
                          key={sIdx}
                          className="rounded-xl border border-border/60 bg-card/60 p-2.5 text-xs"
                        >
                          <div className="flex items-center justify-between gap-2">
                            <span className="font-medium text-foreground">{s.title}</span>
                            {s.url && (s.url.startsWith("http://") || s.url.startsWith("https://")) && (
                              <a
                                href={s.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-1 text-primary hover:underline"
                              >
                                Official Portal <ExternalLink className="h-3 w-3" />
                              </a>
                            )}
                          </div>
                          <p className="mt-1 line-clamp-2 text-muted-foreground">{s.snippet}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {m.content && !loading && (
                  <div className="mt-2 flex gap-1 opacity-0 transition group-hover:opacity-100">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        void navigator.clipboard.writeText(m.content);
                        toast.success("Copied to clipboard");
                      }}
                    >
                      <Copy className="mr-1 h-3.5 w-3.5" /> Copy
                    </Button>
                    <Button variant="ghost" size="sm" onClick={regenerate}>
                      <RotateCcw className="mr-1 h-3.5 w-3.5" /> Retry
                    </Button>
                  </div>
                )}
              </div>
            </div>
          ),
        )}

        {loading && (
          <div className="flex items-center gap-3 pl-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-primary animate-pulse">
              <Sun className="h-4 w-4 text-accent" />
            </span>
            <p className="text-sm text-muted-foreground">Avasar is thinking…</p>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-border px-5 py-4">
        <div className="flex items-end gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                void send(input, messages);
              }
            }}
            placeholder="Ask about a scheme, eligibility, documents…"
            rows={2}
            className="min-h-[56px] resize-none rounded-2xl"
          />
          {loading ? (
            <Button
              size="icon"
              variant="secondary"
              aria-label="Stop"
              onClick={() => abortRef.current?.abort()}
            >
              <Square className="h-4 w-4" />
            </Button>
          ) : (
            <Button
              size="icon"
              aria-label="Send message"
              disabled={!input.trim()}
              onClick={() => void send(input, messages)}
            >
              <ArrowUp className="h-4 w-4" />
            </Button>
          )}
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          Avasar provides information based on available government sources. Please verify important
          details on the official website.
        </p>
      </div>
    </div>
  );
}
