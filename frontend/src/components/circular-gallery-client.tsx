"use client";

import { lazy, Suspense, useSyncExternalStore } from "react";
import type { GalleryItem } from "@/data/gallery-items";

// The gallery uses WebGL, so it only renders in the browser.
const CircularGallery = lazy(() => import("./CircularGallery.jsx")) as unknown as React.FC<{
  items: { image: string; text: string }[];
  bend?: number;
  textColor?: string;
  borderRadius?: number;
  scrollEase?: number;
  font?: string;
}>;

const emptySubscribe = () => () => {};

export function CircularGalleryClient({ items }: { items: GalleryItem[] }) {
  const isClient = useSyncExternalStore(
    emptySubscribe,
    () => true,
    () => false
  );

  if (!isClient) return <div className="h-full w-full" />;

  return (
    <Suspense fallback={<div className="h-full w-full" />}>
      <CircularGallery
        items={items.map(({ image, text }) => ({ image, text }))}
        bend={2.5}
        textColor="#ffffff"
        borderRadius={0.06}
        scrollEase={0.03}
      />
    </Suspense>
  );
}
