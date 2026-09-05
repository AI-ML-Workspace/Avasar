export type Scheme = {
  slug: string;
  name: string;
  category: string;
  image: string;
  summary: string;
  description: string;
  eligibility: string[];
  benefits: string[];
  documents: string[];
  howToApply: string[];
  whereToApply: string;
  conditions: string[];
  source: { label: string; url: string };
};

export const categories = [
  "Students",
  "Farmers",
  "Women",
  "Healthcare",
  "Housing",
  "Employment",
  "Financial Support",
  "Small Businesses",
] as const;

export const schemes: Scheme[] = [
  {
    slug: "pm-kisan",
    name: "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
    category: "Farmers",
    image: "/Pradhan_Mantri_Kisan_Samman_Nidhi_mobile_dd1cd5b59b.jpg",
    summary: "Income support of ₹6,000 per year for eligible landholding farmer families.",
    description:
      "A central sector scheme that provides income support to all landholding farmer families, paid in three equal instalments directly into bank accounts.",
    eligibility: [
      "Landholding farmer families with cultivable land in their name",
      "Name recorded in the land records of the State/UT",
      "Excludes income-tax payers, institutional landholders and certain government employees",
    ],
    benefits: ["₹6,000 per year", "Paid in three instalments of ₹2,000", "Direct bank transfer"],
    documents: [
      "Aadhaar card",
      "Land ownership records",
      "Bank account details (Aadhaar-seeded)",
      "Citizenship proof",
    ],
    howToApply: [
      "Register on the PM-KISAN portal or visit your nearest Common Service Centre",
      "Fill the farmer registration form with Aadhaar and land details",
      "Complete e-KYC",
      "Track application status on the portal",
    ],
    whereToApply: "pmkisan.gov.in, Common Service Centres, or the local Patwari/Revenue office",
    conditions: [
      "e-KYC is mandatory to receive instalments",
      "Bank account must be linked with Aadhaar",
    ],
    source: { label: "pmkisan.gov.in", url: "https://pmkisan.gov.in" },
  },
  {
    slug: "pm-scholarship-national",
    name: "National Scholarship Portal Schemes",
    category: "Students",
    image: "/Screenshot 2026-09-05 073522.png",
    summary: "A single window for central and state scholarships for school and college students.",
    description:
      "The National Scholarship Portal hosts pre-matric, post-matric and merit-cum-means scholarships offered by central ministries and states.",
    eligibility: [
      "Students enrolled in a recognised school, college or university",
      "Family income limits vary by scheme (commonly ₹1–8 lakh per year)",
      "Minimum marks in the previous qualifying exam for some schemes",
    ],
    benefits: [
      "Tuition fee support",
      "Maintenance allowance",
      "Annual renewal for continuing students",
    ],
    documents: [
      "Aadhaar card",
      "Income certificate",
      "Caste/category certificate (if applicable)",
      "Previous year marksheet",
      "Bank passbook and institute verification",
    ],
    howToApply: [
      "Register on the National Scholarship Portal with a valid mobile number",
      "Complete the student profile and choose applicable scholarships",
      "Upload documents and submit before the deadline",
      "Get the application verified by your institute",
    ],
    whereToApply: "scholarships.gov.in, plus your institute's scholarship cell",
    conditions: [
      "One application per student per academic year",
      "Aadhaar-seeded bank account required for payment",
    ],
    source: { label: "scholarships.gov.in", url: "https://scholarships.gov.in" },
  },
  {
    slug: "ayushman-bharat-pmjay",
    name: "Ayushman Bharat PM-JAY",
    category: "Healthcare",
    image: "/Screenshot 2026-09-05 073535.png",
    summary: "Health cover of ₹5 lakh per family per year for secondary and tertiary care.",
    description:
      "A health assurance scheme providing cashless treatment at empanelled public and private hospitals for eligible families.",
    eligibility: [
      "Families identified through SECC deprivation criteria",
      "Certain occupational categories in urban areas",
      "State-specific expansions in some states",
    ],
    benefits: [
      "₹5 lakh cover per family per year",
      "Cashless and paperless treatment",
      "Pre and post hospitalisation expenses covered",
    ],
    documents: ["Aadhaar card", "Ration card", "Mobile number", "Ayushman card (once issued)"],
    howToApply: [
      "Check eligibility on the PM-JAY website or via the helpline 14555",
      "Visit a Common Service Centre or empanelled hospital's Ayushman Mitra desk",
      "Complete verification and receive the Ayushman card",
    ],
    whereToApply: "pmjay.gov.in, empanelled hospitals, or Common Service Centres",
    conditions: [
      "Treatment must be taken at empanelled hospitals",
      "Cover is per family, not per member",
    ],
    source: { label: "pmjay.gov.in", url: "https://pmjay.gov.in" },
  },
  {
    slug: "pmay-urban",
    name: "Pradhan Mantri Awas Yojana (Urban)",
    category: "Housing",
    image: "/Screenshot 2026-09-05 073544.png",
    summary: "Assistance for affordable housing for urban families, including interest subsidy.",
    description:
      "Supports construction, purchase or enhancement of houses for eligible urban households through subsidies and affordable housing projects.",
    eligibility: [
      "Household must not own a pucca house anywhere in India",
      "Income category based (EWS, LIG, MIG)",
      "Adult woman ownership or co-ownership preferred",
    ],
    benefits: [
      "Central assistance for house construction",
      "Credit-linked interest subsidy on home loans",
      "Priority for women, SC/ST and differently-abled applicants",
    ],
    documents: [
      "Aadhaar card",
      "Income proof",
      "Property/land documents",
      "Bank account details",
      "Affidavit of no pucca house",
    ],
    howToApply: [
      "Apply online on the PMAY-U portal or at a Common Service Centre",
      "Enter Aadhaar and household details",
      "Submit and note the application number for tracking",
    ],
    whereToApply: "pmay-urban.gov.in or your Urban Local Body office",
    conditions: [
      "Only one benefit per household",
      "House must be completed within the prescribed period",
    ],
    source: { label: "pmay-urban.gov.in", url: "https://pmay-urban.gov.in" },
  },
  {
    slug: "sukanya-samriddhi",
    name: "Sukanya Samriddhi Yojana",
    category: "Women",
    image: "/Screenshot 2026-09-05 073528.png",
    summary: "A small savings scheme for a girl child with attractive interest and tax benefits.",
    description:
      "Parents or guardians can open an account for a girl child below 10 years, building savings for her education and marriage.",
    eligibility: [
      "Girl child below 10 years of age",
      "Opened by a parent or legal guardian",
      "Maximum two accounts per family (exceptions for twins/triplets)",
    ],
    benefits: [
      "Higher interest rate than regular savings",
      "Tax benefits under Section 80C",
      "Partial withdrawal for higher education",
    ],
    documents: [
      "Birth certificate of the girl child",
      "Identity and address proof of guardian",
      "Photographs",
    ],
    howToApply: [
      "Visit a post office or authorised bank branch",
      "Fill the SSY account opening form",
      "Deposit the minimum amount to activate the account",
    ],
    whereToApply: "Any post office or authorised public/private sector bank branch",
    conditions: [
      "Minimum yearly deposit required to keep the account active",
      "Account matures 21 years from opening",
    ],
    source: { label: "nsiindia.gov.in", url: "https://www.nsiindia.gov.in" },
  },
  {
    slug: "mgnrega",
    name: "MGNREGA (Mahatma Gandhi NREGA)",
    category: "Employment",
    image: "/Screenshot 2026-09-05 073558.png",
    summary: "Guaranteed 100 days of wage employment per year for rural households.",
    description:
      "Provides a legal guarantee of at least 100 days of unskilled manual work in a financial year to every rural household that demands it.",
    eligibility: [
      "Adult members of a rural household",
      "Willing to do unskilled manual work",
      "Registered with the local Gram Panchayat",
    ],
    benefits: [
      "100 days of guaranteed wage employment",
      "Notified daily wage paid to a bank/post office account",
      "Unemployment allowance if work is not provided in time",
    ],
    documents: ["Aadhaar card", "Proof of residence", "Photographs", "Bank/post office passbook"],
    howToApply: [
      "Apply for a job card at the Gram Panchayat",
      "Submit a written work demand application",
      "Receive work allocation within 15 days",
    ],
    whereToApply: "Gram Panchayat office; details on nrega.nic.in",
    conditions: [
      "Work is usually provided within 5 km of the village",
      "Wages must be paid within 15 days of work completion",
    ],
    source: { label: "nrega.nic.in", url: "https://nrega.nic.in" },
  },
  {
    slug: "pm-mudra-yojana",
    name: "Pradhan Mantri MUDRA Yojana",
    category: "Small Businesses",
    image: "/Screenshot 2026-09-05 073620.png",
    summary: "Collateral-free loans up to ₹10 lakh for small and micro enterprises.",
    description:
      "Provides loans under Shishu, Kishore and Tarun categories to non-farm micro and small enterprises through banks and NBFCs.",
    eligibility: [
      "Indian citizen running or starting a non-farm micro enterprise",
      "Business plan with a credit need up to ₹10 lakh",
      "No default history with lending institutions",
    ],
    benefits: [
      "Shishu: up to ₹50,000",
      "Kishore: ₹50,000 to ₹5 lakh",
      "Tarun: ₹5 lakh to ₹10 lakh",
      "No collateral required",
    ],
    documents: [
      "Identity and address proof",
      "Business proof/registration",
      "Bank statements",
      "Quotations for machinery or equipment",
    ],
    howToApply: [
      "Prepare a simple business plan",
      "Apply at a bank branch or on the Jan Samarth portal",
      "Submit documents and complete bank verification",
    ],
    whereToApply: "Any bank, NBFC or MFI branch; also udyamimitra.in",
    conditions: [
      "Loan is for income-generating activities only",
      "Interest rates vary by lender",
    ],
    source: { label: "mudra.org.in", url: "https://www.mudra.org.in" },
  },
  {
    slug: "atal-pension-yojana",
    name: "Atal Pension Yojana",
    category: "Financial Support",
    image: "/Screenshot 2026-09-05 073611.png",
    summary: "A guaranteed pension of ₹1,000 to ₹5,000 per month after age 60.",
    description:
      "A pension scheme focused on workers in the unorganised sector, with contributions based on the chosen pension amount and joining age.",
    eligibility: [
      "Indian citizen aged 18 to 40 years",
      "Has a savings bank account",
      "Not an income-tax payer",
    ],
    benefits: [
      "Fixed monthly pension after 60",
      "Pension continues to spouse",
      "Corpus returned to nominee",
    ],
    documents: ["Aadhaar card", "Savings bank account details", "Mobile number"],
    howToApply: [
      "Visit your bank branch or use net banking",
      "Fill the APY registration form",
      "Set up auto-debit for contributions",
    ],
    whereToApply: "Your bank or post office where you hold a savings account",
    conditions: [
      "Contributions are auto-debited monthly, quarterly or half-yearly",
      "Penalties apply for delayed contributions",
    ],
    source: { label: "npscra.nsdl.co.in", url: "https://npscra.nsdl.co.in" },
  },
];

export const getScheme = (slug: string) => schemes.find((s) => s.slug === slug);
