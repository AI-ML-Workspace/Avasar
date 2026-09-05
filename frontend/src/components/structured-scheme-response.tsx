"use client";

import React, { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Building2,
  Users,
  Coins,
  FileText,
  ClipboardList,
  MapPin,
  AlertTriangle,
  ExternalLink,
  Target,
  CheckCircle2,
  Info,
} from "lucide-react";

interface StructuredSchemeResponseProps {
  content: string;
}

/**
 * Sanitize raw HTML tags like <br>, <div>, <span> so they are never printed literally.
 */
function sanitizeRawHtml(text: string): string {
  if (!text) return "";
  return text
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/?(div|span|p|html|body|head|header|footer|section|article)\b[^>]*>/gi, "")
    .replace(/&lt;br\s*\/?&gt;/gi, "\n")
    .replace(/&lt;\/?(div|span|p|html|body)\b[^&]*&gt;/gi, "");
}

import type { Components } from "react-markdown";

/**
 * Custom ReactMarkdown component overrides styled for clean visual section cards
 */
const markdownComponents: Components = {
  h1: ({ children }) => (
    <h1 className="text-lg font-bold text-foreground sm:text-xl border-b border-black pb-2 mb-3">
      {children}
    </h1>
  ),
  h2: ({ children }) => (
    <h2 className="text-base font-bold text-foreground sm:text-lg border-b border-black/80 pb-1.5 mb-2.5">
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-sm font-bold text-foreground sm:text-base mb-2">
      {children}
    </h3>
  ),
  h4: ({ children }) => (
    <h4 className="text-xs font-bold text-foreground uppercase tracking-wider mb-1.5">
      {children}
    </h4>
  ),
  p: ({ children }) => (
    <p className="my-1 text-sm leading-relaxed text-foreground/90 font-normal">
      {children}
    </p>
  ),
  ul: ({ children }) => (
    <ul className="my-2 space-y-2 pl-0.5">
      {children}
    </ul>
  ),
  ol: ({ children }) => (
    <ol className="my-2 space-y-2 pl-0.5 list-none">
      {children}
    </ol>
  ),
  li: ({ children, node }) => {
    const parent = (node as Record<string, unknown> | undefined)?.parent as { tagName?: string } | undefined;
    const isOrdered = parent?.tagName === "ol";

    if (isOrdered) {
      return (
        <li className="flex items-start gap-2.5 text-sm text-foreground">
          <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-[11px] font-bold text-primary border border-black/40">
            •
          </span>
          <div className="flex-1 min-w-0">{children}</div>
        </li>
      );
    }

    return (
      <li className="flex items-start gap-2.5 text-sm text-foreground">
        <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
        <div className="flex-1 min-w-0">{children}</div>
      </li>
    );
  },
  strong: ({ children }) => (
    <strong className="font-semibold text-foreground">{children}</strong>
  ),
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-1.5 font-semibold text-primary hover:text-accent underline underline-offset-2 transition"
    >
      {children}
      <ExternalLink className="h-3 w-3 inline" />
    </a>
  ),
};

type ParsedSection = {
  id: string;
  title: string;
  icon: React.ReactNode;
  content: string;
  type: "scheme_header" | "eligibility" | "benefits" | "documents" | "how_to_apply" | "where_to_apply" | "important_conditions" | "why_relevant" | "official_source" | "general";
};

/**
 * Section Detector: Matches markdown headers/paragraphs to standard government scheme sections
 */
function parseSchemeSections(rawText: string): ParsedSection[] {
  const cleanText = sanitizeRawHtml(rawText);
  if (!cleanText.trim()) return [];

  // Split by markdown headings (e.g. ###, ####, **, or emoji headings)
  const sectionRegex = /(?=\n(?:#{1,4}|\*\*|👥|💰|📄|📝|📍|⚠️|🔗|🎯|🏛️))/gi;
  const rawParts = cleanText.split(sectionRegex).map((s) => s.trim()).filter(Boolean);

  const sections: ParsedSection[] = [];

  rawParts.forEach((part, index) => {
    const lower = part.toLowerCase();

    if (index === 0 && !lower.includes("eligible") && !lower.includes("benefit")) {
      sections.push({
        id: `sec-${index}`,
        title: "Scheme Overview",
        icon: <Building2 className="h-4.5 w-4.5 text-primary shrink-0" />,
        content: part,
        type: "scheme_header",
      });
      return;
    }

    if (lower.includes("eligible") || lower.includes("eligibility") || lower.includes("who is eligible")) {
      sections.push({
        id: `sec-${index}`,
        title: "👥 WHO IS ELIGIBLE?",
        icon: <Users className="h-4.5 w-4.5 text-primary shrink-0" />,
        content: part.replace(/^(?:#{1,4}|\*\*|👥)?\s*(?:who is eligible\??|eligibility)\s*\:?/i, "").trim() || part,
        type: "eligibility",
      });
    } else if (lower.includes("benefit") || lower.includes("benefits") || lower.includes("financial assistance")) {
      sections.push({
        id: `sec-${index}`,
        title: "💰 BENEFITS",
        icon: <Coins className="h-4.5 w-4.5 text-primary shrink-0" />,
        content: part.replace(/^(?:#{1,4}|\*\*|💰)?\s*(?:benefits?|financial assistance)\s*\:?/i, "").trim() || part,
        type: "benefits",
      });
    } else if (lower.includes("document") || lower.includes("required documents")) {
      sections.push({
        id: `sec-${index}`,
        title: "📄 REQUIRED DOCUMENTS",
        icon: <FileText className="h-4.5 w-4.5 text-primary shrink-0" />,
        content: part.replace(/^(?:#{1,4}|\*\*|📄)?\s*(?:required documents?|documents?)\s*\:?/i, "").trim() || part,
        type: "documents",
      });
    } else if (lower.includes("how to apply") || lower.includes("application process")) {
      sections.push({
        id: `sec-${index}`,
        title: "📝 HOW TO APPLY",
        icon: <ClipboardList className="h-4.5 w-4.5 text-primary shrink-0" />,
        content: part.replace(/^(?:#{1,4}|\*\*|📝)?\s*(?:how to apply|application process)\s*\:?/i, "").trim() || part,
        type: "how_to_apply",
      });
    } else if (lower.includes("where to apply") || lower.includes("portal") || lower.includes("location")) {
      sections.push({
        id: `sec-${index}`,
        title: "📍 WHERE TO APPLY",
        icon: <MapPin className="h-4.5 w-4.5 text-primary shrink-0" />,
        content: part.replace(/^(?:#{1,4}|\*\*|📍)?\s*(?:where to apply|application location)\s*\:?/i, "").trim() || part,
        type: "where_to_apply",
      });
    } else if (lower.includes("important condition") || lower.includes("condition") || lower.includes("note")) {
      sections.push({
        id: `sec-${index}`,
        title: "⚠️ IMPORTANT CONDITIONS",
        icon: <AlertTriangle className="h-4.5 w-4.5 text-primary shrink-0" />,
        content: part.replace(/^(?:#{1,4}|\*\*|⚠️)?\s*(?:important conditions?|conditions?)\s*\:?/i, "").trim() || part,
        type: "important_conditions",
      });
    } else if (lower.includes("relevant to you") || lower.includes("why this")) {
      sections.push({
        id: `sec-${index}`,
        title: "🎯 WHY THIS MAY BE RELEVANT TO YOU",
        icon: <Target className="h-4.5 w-4.5 text-amber-700 shrink-0" />,
        content: part.replace(/^(?:#{1,4}|\*\*|🎯)?\s*(?:why this may be relevant to you|why relevant)\s*\:?/i, "").trim() || part,
        type: "why_relevant",
      });
    } else if (lower.includes("official source") || lower.includes("official website")) {
      sections.push({
        id: `sec-${index}`,
        title: "🔗 OFFICIAL SOURCE",
        icon: <ExternalLink className="h-4.5 w-4.5 text-primary shrink-0" />,
        content: part.replace(/^(?:#{1,4}|\*\*|🔗)?\s*(?:official source|official website)\s*\:?/i, "").trim() || part,
        type: "official_source",
      });
    } else {
      sections.push({
        id: `sec-${index}`,
        title: "Information",
        icon: <Info className="h-4.5 w-4.5 text-primary shrink-0" />,
        content: part,
        type: "general",
      });
    }
  });

  return sections;
}

export function StructuredSchemeResponse({ content }: StructuredSchemeResponseProps) {
  const cleanContent = useMemo(() => sanitizeRawHtml(content), [content]);

  const isFallbackMessage = useMemo(() => {
    return (
      cleanContent.includes("no matching scheme details were found") ||
      cleanContent.includes("not enough information to answer")
    );
  }, [cleanContent]);

  // Split response into distinct scheme cards if multiple schemes exist in markdown
  const schemeBlocks = useMemo(() => {
    if (!cleanContent) return [];
    
    // Split by horizontal rules (e.g. \n---\n or \n***\n)
    const rawBlocks = cleanContent
      .split(/\n\s*[-*_]{3,}\s*\n/)
      .map((b) => b.trim())
      .filter(Boolean);

    return rawBlocks;
  }, [cleanContent]);

  if (isFallbackMessage) {
    return (
      <div className="rounded-2xl border border-black bg-card p-5 shadow-xs">
        <div className="flex items-start gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-secondary text-primary border border-black/60">
            <Info className="h-5 w-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-foreground">
              Verified Government Records Notice
            </h4>
            <p className="mt-1.5 text-sm text-foreground/90 leading-relaxed">
              {cleanContent}
            </p>
            <p className="mt-2.5 text-xs text-muted-foreground">
              💡 Tip: Try asking specifically about scheme names like <em>PM-Kisan</em>, <em>Ayushman Bharat</em>, or <em>PM MUDRA</em>.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {schemeBlocks.map((block, bIdx) => {
        const parsedSections = parseSchemeSections(block);

        return (
          <div
            key={bIdx}
            className="rounded-3xl border border-black bg-card shadow-soft overflow-hidden"
          >
            {/* Top Card Accent */}
            <div className="h-1 w-full bg-primary" />

            <div className="p-5 sm:p-6 space-y-4">
              {parsedSections.map((sec) => (
                <div
                  key={sec.id}
                  className={`rounded-2xl border border-black p-4 sm:p-5 shadow-xs transition ${
                    sec.type === "why_relevant"
                      ? "bg-secondary/80 border-black"
                      : "bg-card/90"
                  }`}
                >
                  {sec.type !== "scheme_header" && sec.type !== "general" && (
                    <div className="flex items-center gap-2 border-b border-black/40 pb-2 mb-3">
                      {sec.icon}
                      <h4 className="text-xs font-bold text-foreground uppercase tracking-wider">
                        {sec.title}
                      </h4>
                    </div>
                  )}

                  <div className="prose prose-sm max-w-none text-foreground prose-headings:text-foreground prose-strong:text-foreground">
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                      {sec.content}
                    </ReactMarkdown>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
