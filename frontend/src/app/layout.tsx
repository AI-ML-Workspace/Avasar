import type { Metadata } from "next";
import { Figtree } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";

const figtree = Figtree({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-figtree",
});

export const metadata: Metadata = {
  title: "Avasar — Government benefits, in your language",
  description:
    "Avasar is a multilingual assistant that helps Indian citizens discover government schemes, check eligibility, documents and how to apply.",
  openGraph: {
    title: "Avasar — Government benefits, in your language",
    description:
      "Ask in your own language and get clear answers about Indian government schemes, eligibility, benefits and how to apply.",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Avasar — Government benefits, in your language",
    description: "Multilingual AI assistant for Indian government schemes.",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={figtree.variable}>
      <body className="font-sans antialiased">
        {children}
        <Toaster position="top-center" />
      </body>
    </html>
  );
}
