// Cards shown in the circular gallery on the homepage.
// Replaced external Unsplash URLs with local scheme images uploaded in public/
export type GalleryItem = {
  image: string;
  text: string;
  href: string;
};

export const galleryItems: GalleryItem[] = [
  {
    image: "/Screenshot 2026-09-05 073522.png",
    text: "Students",
    href: "/schemes?category=Students",
  },
  {
    image: "/Pradhan_Mantri_Kisan_Samman_Nidhi_mobile_dd1cd5b59b.jpg",
    text: "Farmers",
    href: "/schemes?category=Farmers",
  },
  {
    image: "/Screenshot 2026-09-05 073528.png",
    text: "Women",
    href: "/schemes?category=Women",
  },
  {
    image: "/Screenshot 2026-09-05 073535.png",
    text: "Healthcare",
    href: "/schemes?category=Healthcare",
  },
  {
    image: "/Screenshot 2026-09-05 073544.png",
    text: "Housing",
    href: "/schemes?category=Housing",
  },
  {
    image: "/Screenshot 2026-09-05 073558.png",
    text: "Employment",
    href: "/schemes?category=Employment",
  },
  {
    image: "/Screenshot 2026-09-05 073611.png",
    text: "Financial Support",
    href: "/schemes?category=Financial Support",
  },
  {
    image: "/Screenshot 2026-09-05 073620.png",
    text: "Small Businesses",
    href: "/schemes?category=Small Businesses",
  },
];
