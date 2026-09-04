// Cards shown in the circular gallery on the homepage.
// Edit this list any time — change the image URL, the label, or the link.
export type GalleryItem = {
  image: string;
  text: string;
  href: string;
};

export const galleryItems: GalleryItem[] = [
  {
    image:
      "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=900&q=80",
    text: "Students",
    href: "/schemes?category=Students",
  },
  {
    image:
      "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=900&q=80",
    text: "Farmers",
    href: "/schemes?category=Farmers",
  },
  {
    image:
      "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=900&q=80",
    text: "Women",
    href: "/schemes?category=Women",
  },
  {
    image:
      "https://images.unsplash.com/photo-1538108149393-fbbd81895907?auto=format&fit=crop&w=900&q=80",
    text: "Healthcare",
    href: "/schemes?category=Healthcare",
  },
  {
    image:
      "https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=900&q=80",
    text: "Housing",
    href: "/schemes?category=Housing",
  },
  {
    image:
      "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=900&q=80",
    text: "Employment",
    href: "/schemes?category=Employment",
  },
  {
    image:
      "https://images.unsplash.com/photo-1554224155-6726b3ff858f?auto=format&fit=crop&w=900&q=80",
    text: "Financial Support",
    href: "/schemes?category=Financial Support",
  },
  {
    image:
      "https://images.unsplash.com/photo-1556740738-b6a63e27c4df?auto=format&fit=crop&w=900&q=80",
    text: "Small Businesses",
    href: "/schemes?category=Small Businesses",
  },
];
