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
  "Social Security",
] as const;

export const schemes: Scheme[] = [
  {
    "slug": "atal-innovation-mission",
    "name": "Atal Innovation Mission (AIM)",
    "category": "Small Businesses",
    "image": "/images/categories/business.svg",
    "summary": "Atal Innovation Mission is a flagship initiative set up by NITI Aayog to promote a culture of innovation and entrepreneurship across schools, universities, research institutions, MSMEs, and industry sectors in India.",
    "description": "Atal Innovation Mission is a flagship initiative set up by NITI Aayog to promote a culture of innovation and entrepreneurship across schools, universities, research institutions, MSMEs, and industry sectors in India.",
    "eligibility": [
      "Schools, higher educational institutions, research organizations, startups, incubators, and individual innovators who participate in specific AIM initiatives (e.g., Atal Tinkering Labs, Atal Incubation Centres, AIM Challenges)."
    ],
    "benefits": [
      "Grant-in-aid support of up to ₹20 lakh for schools to establish Atal Tinkering Labs (ATL) for fostering STEM problem-solving skills among students.",
      "Financial assistance of up to ₹10 crore to establish or scale world-class Atal Incubation Centres (AICs) for supporting startups.",
      "Seed funding and prototyping opportunities through Atal New India Challenges (ANIC) and ARISE challenges for MSMEs/startups."
    ],
    "documents": [
      "Institutional Registration Certificate / UDISE Code (for schools/colleges)",
      "PAN and GST registration details (for startups/incubators)",
      "Audited financial statements and infrastructure availability proof",
      "Detailed proposal outlining innovation roadmap and objectives"
    ],
    "howToApply": [
      "Institutions, schools, incubators, and startups submit online proposals/applications through specific call for applications hosted on the official AIM portal (aim.gov.in) during active application windows."
    ],
    "whereToApply": "Institutions, schools, incubators, and startups submit online proposals/applications through specific call for applications hosted on the official AIM",
    "conditions": [
      "AIM is an umbrella institutional initiative; individual benefits are disbursed only to qualified institutions, startups, or challenge winners, not as general citizen cash grants.",
      "Grants-in-aid are milestone-based and monitored strictly through evaluation committees."
    ],
    "source": {
      "label": "Atal Innovation Mission Portal",
      "url": "https://aim.gov.in/"
    }
  },
  {
    "slug": "atal-pension-yojana",
    "name": "Atal Pension Yojana (APY)",
    "category": "Social Security",
    "image": "/images/categories/social.svg",
    "summary": "Atal Pension Yojana is a government-backed voluntary pension scheme focused mainly on unorganized sector workers, providing a guaranteed monthly pension after attaining 60 years of age.",
    "description": "Atal Pension Yojana is a government-backed voluntary pension scheme focused mainly on unorganized sector workers, providing a guaranteed monthly pension after attaining 60 years of age.",
    "eligibility": [
      "Indian citizens aged between 18 and 40 years having a savings bank account or post office account, who are not income tax payers."
    ],
    "benefits": [
      "Guaranteed minimum monthly pension of ₹1,000, ₹2,000, ₹3,000, ₹4,000, or ₹5,000 per month starting at age 60, depending on the subscriber's contribution amount.",
      "Same pension amount paid to the spouse upon the subscriber's death.",
      "Return of accumulated pension corpus to the nominee upon the death of both subscriber and spouse."
    ],
    "documents": [
      "Savings Bank Account / Post Office Account details",
      "Aadhaar Card",
      "Active mobile number",
      "Nominee details"
    ],
    "howToApply": [
      "Eligible individuals can join APY by submitting an APY registration form to their bank or post office branch where they hold a savings account, or online via bank netbanking / auto-debit registration facilities."
    ],
    "whereToApply": "Eligible individuals can join APY by submitting an APY registration form to their bank or post office branch where they hold a savings account, or onl",
    "conditions": [
      "Subscriber must be between 18 and 40 years of age at the time of joining.",
      "From October 1, 2022, any citizen who is or has been an income tax payer is not eligible to join APY.",
      "Contributions are automatically debited from the subscriber's bank account monthly, quarterly, or half-yearly.",
      "Premature exit is permitted only under exceptional circumstances such as terminal illness or death of the subscriber."
    ],
    "source": {
      "label": "myScheme - APY / PFRDA",
      "url": "https://www.myscheme.gov.in/schemes/apy"
    }
  },
  {
    "slug": "ayushman-bharat-pmjay",
    "name": "Ayushman Bharat – Pradhan Mantri Jan Arogya Yojana (PM-JAY)",
    "category": "Healthcare",
    "image": "/images/categories/healthcare.svg",
    "summary": "PM-JAY is the world's largest government-funded health assurance scheme, offering cashless secondary and tertiary inpatient medical care coverage to vulnerable socio-economic families and senior citizens aged 70 and above.",
    "description": "PM-JAY is the world's largest government-funded health assurance scheme, offering cashless secondary and tertiary inpatient medical care coverage to vulnerable socio-economic families and senior citizens aged 70 and above.",
    "eligibility": [
      "Families identified based on deprivation and occupational criteria in SECC 2011 data, active state health insurance scheme databases, and all senior citizens aged 70 years and above (Ayushman Vaya Vandana Card)."
    ],
    "benefits": [
      "Cashless health insurance coverage up to ₹5,00,000 per family per year for secondary and tertiary care hospitalization.",
      "Covers medical examination, treatment, consultations, pre-hospitalization (up to 3 days), post-hospitalization (up to 15 days), diagnostics, medicine, and ICU charges.",
      "No restriction on family size, age, or gender.",
      "Portability of benefits across empaneled public and private hospitals across India."
    ],
    "documents": [
      "Aadhaar Card",
      "Ration Card / PM-JAY letter / Family ID proof",
      "Active mobile number for OTP authentication"
    ],
    "howToApply": [
      "Eligible individuals can check their status online at pmjay.gov.in or beneficiary.nha.gov.in, and generate/download their Ayushman Card through the portal, mobile app, or at empaneled hospitals / CSCs via Ayushman Mitra verification."
    ],
    "whereToApply": "Eligible individuals can check their status online at pmjay.gov.in or beneficiary.nha.gov.in, and generate/download their Ayushman Card through the po",
    "conditions": [
      "Pre-existing medical conditions are covered from day one of enrollment.",
      "Treatment is cashless and paperless at all empaneled public and private healthcare providers.",
      "Senior citizens aged 70+ receive a dedicated Ayushman Vaya Vandana Card regardless of income level."
    ],
    "source": {
      "label": "National Health Authority - PM-JAY Portal",
      "url": "https://pmjay.gov.in/"
    }
  },
  {
    "slug": "beti-bachao-beti-padhao",
    "name": "Beti Bachao Beti Padhao (BBBP)",
    "category": "Women",
    "image": "/images/categories/women.svg",
    "summary": "Beti Bachao Beti Padhao is a joint flagship national programme implemented across India to address the declining Child Sex Ratio (CSR), eliminate gender-biased sex selection, and promote the education, protection, and empowerment of the girl child.",
    "description": "Beti Bachao Beti Padhao is a joint flagship national programme implemented across India to address the declining Child Sex Ratio (CSR), eliminate gender-biased sex selection, and promote the education, protection, and empowerment of the girl child.",
    "eligibility": [
      "This is a nationwide government multi-sectoral awareness and advocacy programme rather than a direct cash-transfer scheme for individual applicants."
    ],
    "benefits": [
      "Drives multi-sectoral action and community awareness to prevent female foeticide and improve Child Sex Ratio at Birth.",
      "Ensures survival, protection, and mandatory secondary education for girl children.",
      "Promotes institutional deliveries, girl-child enrollment, retention, and nutritional support through convergent district interventions."
    ],
    "documents": [],
    "howToApply": [
      "Not applicable. BBBP is a national campaign and inter-ministerial programme; there is no individual application procedure or direct money transfer under BBBP itself."
    ],
    "whereToApply": "Not applicable. BBBP is a national campaign and inter-ministerial programme; there is no individual application procedure or direct money transfer und",
    "conditions": [
      "BBBP is a programmatic initiative for social change and district-level convergence; it does not distribute direct financial payouts or cash awards to citizens.",
      "Citizens are advised to beware of fraudulent schemes or false forms claiming to distribute money under the name of Beti Bachao Beti Padhao."
    ],
    "source": {
      "label": "Ministry of Women and Child Development",
      "url": "https://wcd.gov.in/women/beti-bachao-beti-padhao"
    }
  },
  {
    "slug": "cgtmse",
    "name": "Credit Guarantee Fund Trust for Micro and Small Enterprises (CGTMSE)",
    "category": "Small Businesses",
    "image": "/images/categories/business.svg",
    "summary": "CGTMSE was set up jointly by the Ministry of MSME and Small Industries Development Bank of India (SIDBI) to facilitate collateral-free credit flow to the micro and small enterprise sector.",
    "description": "CGTMSE was set up jointly by the Ministry of MSME and Small Industries Development Bank of India (SIDBI) to facilitate collateral-free credit flow to the micro and small enterprise sector. The trust guarantees loans sanctioned by Member Lending Institutions (MLIs) to new and existing Micro and Small Enterprises (MSEs) without requiring third-party guarantees or collateral security.",
    "eligibility": [
      "New and existing Micro and Small Enterprises (both manufacturing and service enterprises) as defined under the MSMED Act. Retail trade, educational institutions, training institutes, and self-help groups (SHGs) are also covered up to specified limits. Medium enterprises are excluded."
    ],
    "benefits": [
      "Collateral-free and third-party guarantee-free credit facilities (both fund-based term loan/working capital and non-fund-based) up to Rs 5 crore per borrowing unit.",
      "Guarantee cover up to 85% for micro-enterprises for loans up to Rs 5 lakh.",
      "Guarantee cover up to 85% for loans to women entrepreneurs, SC/ST entrepreneurs, and units located in NER and UTs of J&K and Ladakh.",
      "Guarantee cover up to 75% for general category MSE borrowers for credit facilities up to Rs 5 crore.",
      "Reduced annual guarantee fees starting from 0.37% for micro-enterprises."
    ],
    "documents": [
      "Udyam Registration Certificate",
      "Detailed Project Report / Business Plan",
      "KYC documents of promoters (PAN, Aadhaar)",
      "Financial statements, IT returns, and bank statements of the enterprise",
      "Quotations for machinery/equipment and working capital assessment"
    ],
    "howToApply": [
      "Borrowers do not apply to CGTMSE directly. The entrepreneur approaches a registered Member Lending Institution (Scheduled Commercial Bank, Regional Rural Bank, Small Finance Bank, or NBFC) with a viable project proposal. If the bank sanctions the loan without collateral, the lending institution applies directly to CGTMSE for the guarantee cover."
    ],
    "whereToApply": "Borrowers do not apply to CGTMSE directly. The entrepreneur approaches a registered Member Lending Institution (Scheduled Commercial Bank, Regional Ru",
    "conditions": [
      "Credit evaluation and sanctioning discretion remains solely with the Member Lending Institution.",
      "Guarantee cover is revoked if the lending institution charges interest higher than the prescribed cap over their benchmark lending rate.",
      "Medium enterprises (investment in plant & machinery above Rs 10 crore or turnover above Rs 50 crore) are not eligible."
    ],
    "source": {
      "label": "Credit Guarantee Fund Trust for Micro and Small Enterprises (CGTMSE)",
      "url": "https://www.cgtmse.in/"
    }
  },
  {
    "slug": "day-nrlm",
    "name": "Deendayal Antyodaya Yojana - National Rural Livelihoods Mission (DAY-NRLM)",
    "category": "Women",
    "image": "/images/categories/women.svg",
    "summary": "DAY-NRLM (Aajeevika) is a poverty alleviation project implemented by the Ministry of Rural Development.",
    "description": "DAY-NRLM (Aajeevika) is a poverty alleviation project implemented by the Ministry of Rural Development. It aims to reduce poverty by mobilizing rural poor households into Self-Help Groups (SHGs) and federated institutions, enabling them to access gainful self-employment, skilled wage employment opportunities, and financial services, building sustainable livelihoods.",
    "eligibility": [
      "Rural poor households, with priority given to women, Scheduled Castes, Scheduled Tribes, vulnerable tribal groups, single women, disabled persons, and landless laborers. At least one woman member from each identified poor household is mobilized into a Self Help Group."
    ],
    "benefits": [
      "Revolving Fund (RF) of Rs 10,000 to Rs 15,000 per eligible SHG to catalyze credit habits and meet immediate needs.",
      "Community Investment Fund (CIF) provided to Village Organizations for lending to SHGs for livelihood activities.",
      "Interest Subvention on prompt bank loan repayment, bringing the effective interest rate down to 7% (and further 4% in designated intensive districts) for loans up to Rs 3 lakh.",
      "Capacity building, financial literacy, and livelihood training for members.",
      "Support for farm and non-farm micro-enterprises and value chain collectives."
    ],
    "documents": [
      "Aadhaar Card of members",
      "Group bank account opening documents (resolution of SHG, member KYC)",
      "Voter ID / proof of residence in the village",
      "BPL or SECC deprivation certificate / Participatory Identification of the Poor (PIP) record"
    ],
    "howToApply": [
      "Interested rural women can join or form a local Self Help Group (SHG) comprising 10-20 members through their local Village Organization (VO), Gram Panchayat, or Community Resource Persons (CRPs) designated under the state rural livelihood mission."
    ],
    "whereToApply": "Interested rural women can join or form a local Self Help Group (SHG) comprising 10-20 members through their local Village Organization (VO), Gram Pan",
    "conditions": [
      "SHG must follow the 'Panchasutra' principles: regular meetings, regular savings, regular internal lending, timely repayment, and up-to-date book of accounts.",
      "Interest subvention is contingent on timely and regular loan repayments without default.",
      "Funding flows through community institutions and banks, not directly to individuals."
    ],
    "source": {
      "label": "Deendayal Antyodaya Yojana - NRLM Portal",
      "url": "https://aajeevika.gov.in/"
    }
  },
  {
    "slug": "ddu-grameen-kaushalya",
    "name": "Deen Dayal Upadhyaya Grameen Kaushalya Yojana (DDU-GKY)",
    "category": "Employment",
    "image": "/images/categories/employment.svg",
    "summary": "DDU-GKY (also called Aajeevika Skills) is a placement-linked skill development programme under the Ministry of Rural Development for rural poor youth aged 15–35 years.",
    "description": "DDU-GKY (also called Aajeevika Skills) is a placement-linked skill development programme under the Ministry of Rural Development for rural poor youth aged 15–35 years. It aims to diversify the income sources of rural families and create pathways for sustainable livelihoods through skills training, placement in wage employment, and post-placement support.",
    "eligibility": [
      "Rural youth aged 15–35 years from poor rural families (BPL or SECC-identified). Upper age limit is relaxed to 45 years for SC/ST, Minorities, PwD, women, and ex-servicemen. Priority is given to MGNREGA beneficiaries, SHG members and their children, and families below poverty line."
    ],
    "benefits": [
      "Free residential skills training of minimum 576 hours (around 3 months) across 250+ trades such as retail, construction, healthcare, apparel, IT, and hospitality.",
      "Training includes English language skills, computer literacy, and soft skills.",
      "Mandatory minimum 70% placement in formal sector jobs after training.",
      "Minimum wage guaranteed at Rs 6,000 per month (Rs 8,500 in urban areas and overseas).",
      "Post-placement support and tracking for 6 months to ensure retention.",
      "Accommodation, meals, and transport arranged during residential training.",
      "Overseas placement support for eligible candidates."
    ],
    "documents": [
      "Aadhaar Card",
      "Age proof (birth certificate, school certificate, Aadhaar)",
      "BPL certificate / SECC data verification",
      "Caste certificate (if applicable for age relaxation)",
      "Bank account details",
      "Photograph",
      "Educational qualification documents"
    ],
    "howToApply": [
      "Interested candidates can apply through Project Implementing Agencies (PIAs) empanelled by the state. Applications can also be made at block-level Rural Development offices or state SRLM (State Rural Livelihood Mission) offices. The AAJEEVIKA portal and state helplines provide information on ongoing training batches."
    ],
    "whereToApply": "Interested candidates can apply through Project Implementing Agencies (PIAs) empanelled by the state. Applications can also be made at block-level Rur",
    "conditions": [
      "The programme is placement-linked; training providers are paid only if trainees are placed in jobs.",
      "Candidates must complete the full training programme and pass the assessment to receive placement assistance.",
      "Post-placement salary must be at least the notified minimum wage; DDU-GKY will not count placements below this threshold.",
      "Overseas placement candidates undergo additional documentation and health checks.",
      "Training is residential and free, including boarding, lodging, and food."
    ],
    "source": {
      "label": "DDU-GKY Portal",
      "url": "https://ddugky.gov.in/"
    }
  },
  {
    "slug": "digital-india",
    "name": "Digital India Programme",
    "category": "Social Security",
    "image": "/images/categories/social.svg",
    "summary": "Digital India is a flagship umbrella programme of the Government of India designed to transform the country into a digitally empowered society and knowledge economy through digital infrastructure, digital governance, and digital empowerment of citizens.",
    "description": "Digital India is a flagship umbrella programme of the Government of India designed to transform the country into a digitally empowered society and knowledge economy through digital infrastructure, digital governance, and digital empowerment of citizens.",
    "eligibility": [
      "Digital India is a broad national technology vision and infrastructure programme benefiting all citizens, businesses, and government entities across India; it is not an individual cash-transfer scheme."
    ],
    "benefits": [
      "High-speed broadband network connectivity across Gram Panchayats (BharatNet).",
      "Universal access to digital governance services via digital platforms such as DigiLocker, UMANG, Aadhaar, UPI, eHospital, and MyGov.",
      "Digital literacy initiatives (e.g., PMGDISHA) to train rural citizens in operating digital devices.",
      "Promotes electronics manufacturing, digital payments, and e-commerce across India."
    ],
    "documents": [],
    "howToApply": [
      "Not applicable. Digital India is a national policy framework and umbrella programme. Citizens access individual services provided under Digital India (e.g., DigiLocker, UMANG) by creating accounts on the respective service portals/apps."
    ],
    "whereToApply": "Not applicable. Digital India is a national policy framework and umbrella programme. Citizens access individual services provided under Digital India ",
    "conditions": [
      "Digital India does not offer direct cash application schemes; it provides public digital infrastructure and e-governance platforms.",
      "Individual digital services under Digital India (e.g., DigiLocker, eHospital) have separate free registration procedures."
    ],
    "source": {
      "label": "Digital India Official Portal",
      "url": "https://www.digitalindia.gov.in/"
    }
  },
  {
    "slug": "enam",
    "name": "National Agriculture Market (e-NAM)",
    "category": "Farmers",
    "image": "/images/categories/agriculture.svg",
    "summary": "e-NAM (Electronic National Agriculture Market) is a pan-India electronic trading portal that networks existing Agricultural Produce Market Committees (APMCs) and other market yards to create a unified national market for agricultural commodities.",
    "description": "e-NAM (Electronic National Agriculture Market) is a pan-India electronic trading portal that networks existing Agricultural Produce Market Committees (APMCs) and other market yards to create a unified national market for agricultural commodities. It enables transparent online bidding, better price discovery, reduced post-harvest losses, and prompt payment directly to farmers' bank accounts.",
    "eligibility": [
      "All farmers registered with their nearest APMC-linked e-NAM market yard are eligible to sell their produce on the e-NAM platform. Traders, FPOs (Farmer Producer Organisations), and commission agents can also register. Buyers can be individuals, traders, processors, or exporters registered on the platform."
    ],
    "benefits": [
      "Transparent price discovery through online competitive bidding across multiple buyers.",
      "Access to a wider market beyond local mandi, enabling farmers to sell to buyers across the country.",
      "Direct payment to farmer's bank account within 24–48 hours of sale.",
      "Reduced need for multiple middlemen, improving farmer's net realization.",
      "Online quality assay facilities at integrated mandis to standardize grading.",
      "e-NAM mobile app for real-time price information, trade status, and payment updates."
    ],
    "documents": [
      "Aadhaar Card",
      "Bank account passbook (linked to Aadhaar)",
      "Mobile number",
      "Land records or produce ownership proof",
      "Photograph"
    ],
    "howToApply": [
      "Farmers must register at their nearest APMC mandi that has been integrated with e-NAM (check enam.gov.in for the list of integrated mandis). Registration requires Aadhaar, bank account, and land/produce details. After registration, farmers can bring their produce to the mandi, get it assayed/graded, and participate in online auction. Proceeds are credited to the registered bank account."
    ],
    "whereToApply": "Farmers must register at their nearest APMC mandi that has been integrated with e-NAM (check enam.gov.in for the list of integrated mandis). Registrat",
    "conditions": [
      "e-NAM is only available at APMC-integrated mandis; check the list of integrated mandis on enam.gov.in.",
      "Commodities must be among the notified commodities for each mandi.",
      "The platform does not guarantee a minimum price; price is determined by competitive bidding.",
      "FPOs (Farmer Producer Organisations) can use e-NAM to sell produce of their member farmers collectively."
    ],
    "source": {
      "label": "e-NAM Portal",
      "url": "https://enam.gov.in/"
    }
  },
  {
    "slug": "eshram",
    "name": "e-Shram Portal (National Database of Unorganised Workers)",
    "category": "Social Security",
    "image": "/images/categories/social.svg",
    "summary": "e-Shram is a comprehensive national database of unorganised workers created by the Ministry of Labour and Employment.",
    "description": "e-Shram is a comprehensive national database of unorganised workers created by the Ministry of Labour and Employment. It assigns each registered unorganised worker a unique 12-digit Universal Account Number (UAN) and an e-Shram card, serving as a unified identity for accessing social security schemes, welfare benefits, and disaster relief measures delivered by the central and state governments.",
    "eligibility": [
      "Any unorganised worker aged between 16 and 59 years. Must not be an income tax payee and must not be an active member of EPFO (Employees' Provident Fund) or ESIC (Employees' State Insurance). Includes gig and platform workers, agricultural laborers, construction workers, street vendors, and domestic workers."
    ],
    "benefits": [
      "Issuance of an all-India recognized 12-digit Universal Account Number (UAN) and digital e-Shram identity card.",
      "Seamless portability of social security and welfare benefits across states for migrant workers.",
      "Accidental insurance coverage under PMSBY (Rs 2 lakh for accidental death/permanent disability and Rs 1 lakh for partial disability) for registered eligible workers.",
      "Single window integration for accessing schemes like PM-SYM, PM-JAY, National Career Service, and future relief disbursements.",
      "Integration with Skill India Digital and apprenticeship opportunities."
    ],
    "documents": [
      "Aadhaar Card",
      "Aadhaar-linked active mobile number",
      "Active bank account details (account number, IFSC)"
    ],
    "howToApply": [
      "Self-registration online through the e-Shram portal (eshram.gov.in) using Aadhaar-linked mobile OTP, or via the nearest Common Services Centre (CSC) or State Seva Kendra free of charge."
    ],
    "whereToApply": "Self-registration online through the e-Shram portal (eshram.gov.in) using Aadhaar-linked mobile OTP, or via the nearest Common Services Centre (CSC) o",
    "conditions": [
      "Registration on the e-Shram portal is entirely free of charge for the worker.",
      "Workers must update occupation, address, and mobile number whenever changes occur.",
      "Organized sector formal workers covered under EPFO/ESIC are disqualified from registration."
    ],
    "source": {
      "label": "e-Shram Portal (National Database of Unorganised Workers)",
      "url": "https://eshram.gov.in/"
    }
  },
  {
    "slug": "inspire-scholarship",
    "name": "INSPIRE Scholarship (Innovation in Science Pursuit for Inspired Research)",
    "category": "Students",
    "image": "/images/categories/education.svg",
    "summary": "INSPIRE is a flagship national science programme launched by the Department of Science & Technology (DST) to attract talented youth to study science and pursue a career in research and development.",
    "description": "INSPIRE is a flagship national science programme launched by the Department of Science & Technology (DST) to attract talented youth to study science and pursue a career in research and development. The Scholarship for Higher Education (SHE) component provides scholarships to meritorious students to study natural and basic sciences at the BSc, BS, MSc, and integrated MSc/BS level, fostering a culture of research in India.",
    "eligibility": [
      "Students who have secured admission to BSc, BS, or Integrated MSc/BS programs in natural and basic sciences (Physics, Chemistry, Mathematics, Biology, Statistics, Geology, Astrophysics, Earth Sciences, Atmospheric Sciences, Oceanography, Biochemistry, Bioinformatics, Neuroscience, and allied subjects). Must be in the top 1% of Class 12 Board examination results (state or CBSE/ICSE), or must be a qualifier/ranker in national competitive exams (JEE Advanced, NEET, KVPY, JBNSTS, NTSE, or state-level Olympiads)."
    ],
    "benefits": [
      "Rs 80,000 per year scholarship (payable at Rs 6,667 per month) during BSc/BS/MSc studies.",
      "Additional summer research attachment to INSPIRE Faculty or IISc/IIT/National Laboratories worth Rs 20,000 per attachment.",
      "Scholarship is tenable for up to 5 years (full BSc/BS/MSc or Integrated MSc/BS duration).",
      "Renewal annually based on satisfactory academic performance (minimum CGPA requirement varies by institute)."
    ],
    "documents": [
      "Class 12 mark sheet (Board examination)",
      "Proof of eligibility (rank certificate for JEE/NEET/KVPY/NTSE/Olympiad qualifiers)",
      "Bonafide student certificate from recognized institution",
      "Aadhaar Card",
      "Bank account details",
      "Photograph",
      "Institution admission letter"
    ],
    "howToApply": [
      "Apply online at the INSPIRE portal (online-inspire.gov.in) during the open application window (typically July–September each year). Students must submit proof of Class 12 marks/qualifying exam rank and institute admission letter. Applications are verified and screened by DST. Shortlisted students receive scholarship letters."
    ],
    "whereToApply": "Apply online at the INSPIRE portal (online-inspire.gov.in) during the open application window (typically July–September each year). Students must subm",
    "conditions": [
      "Applicable only for natural and basic science programs at BSc/BS/Integrated MSc/BS level — engineering, medicine, and social science programs are not eligible.",
      "Annual renewal requires maintaining minimum academic performance as specified in the scholarship terms.",
      "Only students at recognized Indian institutions are eligible.",
      "Application window typically closes in September — check the INSPIRE portal for exact dates each year.",
      "INSPIRE also has a Mentorship Programme (for Classes 6–10) and the AORC/Fellowship for PhD — these are separate components."
    ],
    "source": {
      "label": "INSPIRE Portal (DST)",
      "url": "https://online-inspire.gov.in/"
    }
  },
  {
    "slug": "jal-jeevan-mission",
    "name": "Jal Jeevan Mission (JJM)",
    "category": "Social Security",
    "image": "/images/categories/social.svg",
    "summary": "Jal Jeevan Mission is a national flagship programme implemented in partnership with States to assist, empower, and facilitate rural communities in providing Functional Household Tap Connections (FHTC) delivering potable water in adequate quantity and prescribed quality to every rural home.",
    "description": "Jal Jeevan Mission is a national flagship programme implemented in partnership with States to assist, empower, and facilitate rural communities in providing Functional Household Tap Connections (FHTC) delivering potable water in adequate quantity and prescribed quality to every rural home.",
    "eligibility": [
      "JJM is a infrastructure and community-level public utility programme targeting all rural households across all villages in India; it is not an individual cash-transfer scheme."
    ],
    "benefits": [
      "Provision of clean tap water supply (minimum 55 liters per capita per day) to every rural household.",
      "Installation of tap water connections in rural schools, Anganwadi centres, Gram Panchayat buildings, health centres, and community halls.",
      "Community-led water security, rainwater harvesting, greywater treatment, and water quality monitoring through Gram Panchayats / Village Water and Sanitation Committees (VWSC)."
    ],
    "documents": [],
    "howToApply": [
      "Not applicable. JJM is implemented by State Water Supply/Public Health Engineering Departments and Gram Panchayats. Individual citizens do not apply online for cash grants; local tap connections are executed through village piped water supply schemes."
    ],
    "whereToApply": "Not applicable. JJM is implemented by State Water Supply/Public Health Engineering Departments and Gram Panchayats. Individual citizens do not apply o",
    "conditions": [
      "JJM is a community-driven national mission executed at the Village Panchayat level.",
      "Operation and maintenance of in-village water supply infrastructure is managed locally by Gram Panchayats / Pani Samitis."
    ],
    "source": {
      "label": "Jal Jeevan Mission Portal",
      "url": "https://jaljeevanmission.gov.in/"
    }
  },
  {
    "slug": "jan-aushadhi",
    "name": "Pradhan Mantri Bharatiya Janaushadhi Pariyojana (PMBJP) – Jan Aushadhi",
    "category": "Healthcare",
    "image": "/images/categories/healthcare.svg",
    "summary": "PM Jan Aushadhi Pariyojana provides quality generic medicines at affordable prices through dedicated Jan Aushadhi Kendras (stores) set up across India.",
    "description": "PM Jan Aushadhi Pariyojana provides quality generic medicines at affordable prices through dedicated Jan Aushadhi Kendras (stores) set up across India. The scheme aims to make quality medicines accessible to all citizens, especially the poor, by selling generic drugs at prices 50–90% cheaper than branded equivalents, without compromising on quality standards (all medicines are sourced from WHO-GMP certified manufacturers).",
    "eligibility": [
      "All citizens can buy medicines from Jan Aushadhi Kendras at subsidized prices — no means test or eligibility criteria required. Medicines are available to anyone who visits the Kendra. For opening a Jan Aushadhi Kendra: individual, NGO, hospital, trust, or private practitioners can apply with specific requirements."
    ],
    "benefits": [
      "Access to over 2,000 medicines and 300 surgical consumables at prices 50–90% below market rates.",
      "Medicines meet WHO-GMP quality standards — same therapeutic efficacy as branded drugs.",
      "Jan Aushadhi Kendras open across all districts including rural areas.",
      "Savings on chronic disease medicines (diabetes, hypertension, cardiac, etc.) which require lifelong medication."
    ],
    "documents": [
      "Doctor's prescription (for prescription medicines)",
      "No other documents required for purchasing medicines"
    ],
    "howToApply": [
      "No application needed to buy from Jan Aushadhi Kendra. Citizens simply visit the nearest Jan Aushadhi Kendra with a doctor's prescription and purchase medicines. To find the nearest Kendra, use the Jan Aushadhi app or search on janaushadhi.gov.in. For opening a Kendra, apply through the PMBI portal at janaushadhi.gov.in/apply-online."
    ],
    "whereToApply": "No application needed to buy from Jan Aushadhi Kendra. Citizens simply visit the nearest Jan Aushadhi Kendra with a doctor's prescription and purchase",
    "conditions": [
      "Medicines sold at Jan Aushadhi Kendras are generic equivalents of branded medicines — chemically identical active ingredients, meeting the same quality standards.",
      "All medicines are tested at NABL-accredited laboratories.",
      "The Kendra operates as a retail pharmacy on a franchise model — it is privately managed but sells at PMBI-fixed prices.",
      "Availability of specific medicines may vary by Kendra; citizens can check availability through the Jan Aushadhi app."
    ],
    "source": {
      "label": "Jan Aushadhi Portal",
      "url": "https://janaushadhi.gov.in/"
    }
  },
  {
    "slug": "kisan-credit-card",
    "name": "Kisan Credit Card (KCC) Scheme",
    "category": "Farmers",
    "image": "/images/categories/agriculture.svg",
    "summary": "The Kisan Credit Card (KCC) scheme provides farmers with timely and adequate credit support for their agricultural operations, post-harvest expenses, produce maintenance, consumption requirements, and allied activities like animal husbandry and fisheries.",
    "description": "The Kisan Credit Card (KCC) scheme provides farmers with timely and adequate credit support for their agricultural operations, post-harvest expenses, produce maintenance, consumption requirements, and allied activities like animal husbandry and fisheries. It ensures farmers have flexible, revolving credit access at an affordable interest rate through a simplified and bankable credit delivery mechanism.",
    "eligibility": [
      "All farmers — individual/joint borrowers who are owner-cultivators, tenant farmers, oral lessees, and sharecroppers. Self-Help Groups (SHGs) or Joint Liability Groups (JLGs) of farmers including tenant farmers, sharecroppers, etc. Fishermen and animal husbandry farmers are also eligible under extended KCC."
    ],
    "benefits": [
      "Short-term credit for crop cultivation needs based on the scale of finance for notified crops.",
      "Post-harvest expenses, produce marketing loan, and farm asset maintenance included.",
      "Allied activities including animal husbandry and fisheries covered.",
      "Consumption credit of up to 10% of limit for domestic needs.",
      "Interest subvention available: 2% interest subvention and 3% prompt repayment incentive from Government of India, bringing effective interest rate to as low as 4% per annum for loans up to Rs 3 lakh.",
      "Revolving credit facility — repay and redraw as needed within the sanctioned limit.",
      "Personal accident insurance coverage and asset insurance may be bundled."
    ],
    "documents": [
      "Aadhaar Card",
      "Land records / Khasra (for landowners) or tenancy/lease agreement",
      "Photograph",
      "Bank account details",
      "Identity proof (Voter ID, Driving License, or Passport)",
      "Proof of agricultural activity"
    ],
    "howToApply": [
      "Apply at the nearest branch of a Commercial Bank, Regional Rural Bank (RRB), or Cooperative Bank. Application forms are available at bank branches or through PM-KISAN portal (pmkisan.gov.in/KCC.aspx). Farmers with PM-KISAN registration can apply for KCC through simplified process. PM-KISAN beneficiaries can also apply via the PM-KISAN mobile app."
    ],
    "whereToApply": "Apply at the nearest branch of a Commercial Bank, Regional Rural Bank (RRB), or Cooperative Bank. Application forms are available at bank branches or ",
    "conditions": [
      "Credit limit is reviewed and enhanced annually based on updated land holdings, cropping pattern, and cost of cultivation.",
      "The card is valid for 5 years, subject to annual review.",
      "Prompt repayment incentive of 3% reduces effective interest to 4% for loans up to Rs 3 lakh.",
      "Repayment schedule is aligned with crop harvest and marketing cycle.",
      "Non-repayment or default can lead to account becoming NPA and loss of credit facility."
    ],
    "source": {
      "label": "NABARD KCC Guidelines",
      "url": "https://www.nabard.org/"
    }
  },
  {
    "slug": "maulana-azad-national-fellowship",
    "name": "Maulana Azad National Fellowship (MANF)",
    "category": "Students",
    "image": "/images/categories/education.svg",
    "summary": "The Maulana Azad National Fellowship (MANF) was a financial assistance scheme for research scholars belonging to minority communities (Muslim, Christian, Sikh, Buddhist, Parsi, and Jain) pursuing M.",
    "description": "The Maulana Azad National Fellowship (MANF) was a financial assistance scheme for research scholars belonging to minority communities (Muslim, Christian, Sikh, Buddhist, Parsi, and Jain) pursuing M.Phil. and Ph.D. degrees. Note: The Government of India has officially DISCONTINUED the MANF scheme starting from the academic year 2022-23; no new fresh fellowships are awarded.",
    "eligibility": [
      "Scheme is DISCONTINUED for new applicants. Only existing research fellows who were awarded MANF prior to the 2022-23 academic year continue to receive fellowship disbursements until the completion of their tenure, subject to UGC/NTA guidelines and progress reports."
    ],
    "benefits": [
      "For existing fellows prior to discontinuation:",
      "Monthly fellowship allowance equivalent to JRF/SRF rates.",
      "Annual contingency grant for humanities, social sciences, science, and engineering research.",
      "House Rent Allowance (HRA) as per central government norms."
    ],
    "documents": [
      "Discontinued scheme for new applicants.",
      "For existing ongoing beneficiaries: UGC/NTA award letter, progress report, continuation certificate, and Aadhaar-seeded bank details."
    ],
    "howToApply": [
      "New applications are NOT accepted because the scheme was discontinued from the 2022-23 academic year. Existing beneficiaries receive ongoing disbursements through the Aadhaar Payment Bridge System (APBS) / NMDFC based on tenure verification."
    ],
    "whereToApply": "New applications are NOT accepted because the scheme was discontinued from the 2022-23 academic year. Existing beneficiaries receive ongoing disbursem",
    "conditions": [
      "DISCONTINUED SCHEME: Government of India discontinued the MANF scheme effective from FY 2022-23 due to overlap with other central fellowship schemes open to all communities.",
      "No fresh selections or new applications are invited under MANF.",
      "Existing valid fellows continue receiving funds until their approved research tenure expires."
    ],
    "source": {
      "label": "Ministry of Minority Affairs",
      "url": "https://www.minorityaffairs.gov.in/show_content.php?lang=1&level=1&ls_id=100&lid=107"
    }
  },
  {
    "slug": "mgnrega",
    "name": "Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA)",
    "category": "Employment",
    "image": "/images/categories/employment.svg",
    "summary": "MGNREGA is a landmark legislation enacted in 2005 that guarantees 100 days of wage employment per financial year to every rural household whose adult members volunteer to do unskilled manual work.",
    "description": "MGNREGA is a landmark legislation enacted in 2005 that guarantees 100 days of wage employment per financial year to every rural household whose adult members volunteer to do unskilled manual work. It aims to enhance livelihood security in rural areas, create durable assets, and strengthen rural infrastructure through participatory planning.",
    "eligibility": [
      "Any adult member (18 years and above) of a rural household who is willing to do unskilled manual work and is registered under a Job Card. Households must be residing in rural areas and must apply for a Job Card at the local Gram Panchayat."
    ],
    "benefits": [
      "Guaranteed 100 days of employment per household per financial year at the statutory minimum wage (notified wage rates vary by state, typically Rs 220–350 per day).",
      "Work must be provided within 15 days of demand; if not provided, the state government must pay an Unemployment Allowance.",
      "Employment is provided within 5 km of the applicant's home; beyond 5 km, 10% additional wages are paid.",
      "Works focus on water conservation, flood proofing, drought-proofing, land development, plantation, and rural infrastructure.",
      "At least one-third of MGNREGA workers must be women.",
      "Wages paid directly to individual bank/post office accounts within 15 days."
    ],
    "documents": [
      "Aadhaar Card (linked to bank account for wage payment)",
      "Bank or Post Office account passbook",
      "Passport-size photograph",
      "Proof of residence in rural area (ration card, voter ID, or utility bill)"
    ],
    "howToApply": [
      "Eligible households should apply at the local Gram Panchayat office for a Job Card. Once the Job Card is issued (within 15 days), workers can demand employment in writing or orally to the Gram Panchayat. Employment will be provided within 15 days of the written demand."
    ],
    "whereToApply": "Eligible households should apply at the local Gram Panchayat office for a Job Card. Once the Job Card is issued (within 15 days), workers can demand e",
    "conditions": [
      "Benefits are limited to 100 days per household per financial year (April–March).",
      "The scheme covers only unskilled manual work — skilled and semi-skilled work is not included.",
      "Job Cards are issued to households, not individuals; all adult members can work on a single Job Card.",
      "Unemployment Allowance is payable if work is not provided within 15 days: 1/4th of wage rate for the first 30 days, 1/2 wage rate thereafter.",
      "Social audit of works is mandatory and governed by state Social Audit Units."
    ],
    "source": {
      "label": "MGNREGA Official Portal",
      "url": "https://nrega.nic.in/"
    }
  },
  {
    "slug": "mission-indradhanush",
    "name": "Mission Indradhanush",
    "category": "Healthcare",
    "image": "/images/categories/healthcare.svg",
    "summary": "Mission Indradhanush, launched in 2014, aims to ensure full immunization of all children under 2 years and pregnant women who are either unvaccinated or partially vaccinated, targeting the missed and left-out children.",
    "description": "Mission Indradhanush, launched in 2014, aims to ensure full immunization of all children under 2 years and pregnant women who are either unvaccinated or partially vaccinated, targeting the missed and left-out children. It covers 12 vaccine-preventable diseases: Diphtheria, Whooping Cough, Tetanus, Polio, Tuberculosis, Hepatitis B, Meningitis & Pneumonia (due to Haemophilus influenzae type b), Japanese Encephalitis (in select districts), Rotavirus Diarrhea, Rubella, and Pneumococcal Pneumonia. The Intensified Mission Indradhanush (IMI) targets harder-to-reach areas.",
    "eligibility": [
      "All children aged 0–2 years (up to 23 months) who have missed any dose of vaccines under the Universal Immunization Programme (UIP), and pregnant women who have not received Tetanus-Diphtheria (Td) vaccine. No income or registration criteria — available to all."
    ],
    "benefits": [
      "Free vaccination against 12 vaccine-preventable diseases.",
      "Protection covers: BCG (TB), OPV (Polio), Pentavalent (DPT-HepB-Hib), IPV, Measles-Rubella, PCV (Pneumococcal), Rotavirus, and JE (select districts).",
      "Door-to-door mobilization and outreach sessions in underserved areas, migration sites, and high-risk populations.",
      "Maintenance of vaccination records in the Mother and Child Tracking System (MCTS)."
    ],
    "documents": [
      "Mother and Child Protection (MCP) Card / Immunization Card",
      "Aadhaar Card (helpful but not mandatory for immunization)",
      "No other documents required"
    ],
    "howToApply": [
      "No formal application needed. Eligible children and pregnant women can access free immunization at nearest government health sub-centres, PHCs, CHCs, District Hospitals, or through outreach sessions during Mission Indradhanush rounds. ASHA workers and ANMs conduct mobilization and can guide families to nearest vaccination sessions. Track vaccination at cowin.gov.in or by visiting nearest health facility."
    ],
    "whereToApply": "No formal application needed. Eligible children and pregnant women can access free immunization at nearest government health sub-centres, PHCs, CHCs, ",
    "conditions": [
      "Vaccination is voluntary but strongly recommended as the most effective public health intervention for child survival.",
      "Follow the prescribed vaccination schedule on the MCP card — doses missed should be completed at the earliest.",
      "Special Mission Indradhanush rounds are conducted periodically; watch for announcements at local health centres.",
      "The scheme covers children missed under the routine UIP — regular UIP immunization at PHCs continues throughout the year."
    ],
    "source": {
      "label": "Ministry of Health and Family Welfare",
      "url": "https://nhm.gov.in/index4.php?lang=1&level=0&linkid=459&lid=3660"
    }
  },
  {
    "slug": "mission-shakti",
    "name": "Mission Shakti",
    "category": "Women",
    "image": "/images/categories/women.svg",
    "summary": "Mission Shakti is an umbrella scheme launched by the Ministry of Women and Child Development for the safety, security, and empowerment of women.",
    "description": "Mission Shakti is an umbrella scheme launched by the Ministry of Women and Child Development for the safety, security, and empowerment of women. It operates in mission mode with two distinct sub-schemes: 'Sambal' (focusing on safety and security through One Stop Centres, Women Helpline 181, Beti Bachao Beti Padhao, and Nari Adalats) and 'Samarthya' (focusing on empowerment through Ujjawala, Swadhar Greh, Working Women Hostels, National Creche Scheme, and Pradhan Mantri Matru Vandana Yojana).",
    "eligibility": [
      "All Indian women and adolescent girls, with targeted interventions for vulnerable, marginalized, and distress-affected women, working mothers, and pregnant/lactating women."
    ],
    "benefits": [
      "Integrated 24x7 emergency response, legal counsel, and shelter support under the Sambal sub-scheme.",
      "Financial assistance and maternity benefit transfers under the Samarthya component (PMMVY).",
      "Affordable, secure accommodation for working women with day-care facilities for children in urban and rural areas.",
      "Community-level alternative dispute resolution via Nari Adalats.",
      "Institutional care and rehabilitation support for destitute women, survivors of trafficking, and widows."
    ],
    "documents": [
      "Aadhaar Card of the woman applicant",
      "Bank account passbook linked with Aadhaar (for direct benefit transfer components)",
      "Component-specific documentation (e.g., employment letter for working women hostels, pregnancy registration for PMMVY)"
    ],
    "howToApply": [
      "Depending on the specific component, beneficiaries access services via local Anganwadi Centres, One Stop Centres, the 181 helpline, or state social welfare departments. For PMMVY benefits, online registration is done via pmmvy.wcd.gov.in."
    ],
    "whereToApply": "Depending on the specific component, beneficiaries access services via local Anganwadi Centres, One Stop Centres, the 181 helpline, or state social we",
    "conditions": [
      "Mission Shakti functions as an umbrella umbrella framework coordinating state and central allocations.",
      "Sambal components are 100% centrally funded, while Samarthya components follow standard 60:40 Centre-State cost sharing (90:10 for NE/Himalayan states).",
      "Direct financial transfers require active Aadhaar Seeding with the recipient's bank account."
    ],
    "source": {
      "label": "Ministry of Women and Child Development Guidelines for Mission Shakti",
      "url": "https://wcd.nic.in/acts/guidelines-mission-shakti"
    }
  },
  {
    "slug": "mudra-yojana",
    "name": "Pradhan Mantri MUDRA Yojana (PMMY)",
    "category": "Small Businesses",
    "image": "/images/categories/business.svg",
    "summary": "Pradhan Mantri MUDRA Yojana (PMMY) provides collateral-free loans up to ₹10 lakh (extended up to ₹20 lakh under Tarun Plus for past successful borrowers) to non-corporate, non-farm small and micro-enterprises to enable income generation in manufacturing, trading, services, and agriculture-allied sectors.",
    "description": "Pradhan Mantri MUDRA Yojana (PMMY) provides collateral-free loans up to ₹10 lakh (extended up to ₹20 lakh under Tarun Plus for past successful borrowers) to non-corporate, non-farm small and micro-enterprises to enable income generation in manufacturing, trading, services, and agriculture-allied sectors.",
    "eligibility": [
      "Any Indian citizen who has a non-farm business plan for an income-generating activity such as manufacturing, processing, trading, or service sector, and whose credit requirement is up to the specified loan limits."
    ],
    "benefits": [
      "Collateral-free business credit provided across three categories:",
      "Shishu: Loans up to ₹50,000 for early-stage micro enterprises.",
      "Kishore: Loans above ₹50,000 and up to ₹5 lakh for expanding micro enterprises.",
      "Tarun: Loans above ₹5 lakh and up to ₹10 lakh (with Tarun Plus up to ₹20 lakh for qualified repeat borrowers).",
      "No processing fee for Shishu and Kishore category loans."
    ],
    "documents": [
      "Identity proof (Aadhaar Card, Voter ID, PAN Card, Driving License, Passport)",
      "Residence proof (Utility bill, Aadhaar Card, Passport)",
      "Business identity and address proof (Registration certificate, license, tax registration)",
      "Proof of ownership / tenancy of business premises",
      "Passbook / Bank statements for the last 6 months",
      "Quotations of machinery / equipment to be purchased (if applicable)"
    ],
    "howToApply": [
      "Applicants can apply online through the JanSamarth or UdyamiMitra portal, or directly at commercial banks, Regional Rural Banks (RRBs), Small Finance Banks, MFIs, or NBFCs by submitting the MUDRA loan application form."
    ],
    "whereToApply": "Applicants can apply online through the JanSamarth or UdyamiMitra portal, or directly at commercial banks, Regional Rural Banks (RRBs), Small Finance ",
    "conditions": [
      "Loans are provided through partner lending institutions (commercial banks, RRBs, SFBs, MFIs, NBFCs); MUDRA itself does not directly disburse loans to individuals.",
      "No collateral security is required.",
      "Repayment terms range up to 5 years depending on the loan structure and cash flows."
    ],
    "source": {
      "label": "MUDRA Official Website",
      "url": "https://www.mudra.org.in/"
    }
  },
  {
    "slug": "naps",
    "name": "National Apprenticeship Promotion Scheme (NAPS)",
    "category": "Employment",
    "image": "/images/categories/employment.svg",
    "summary": "NAPS was launched by the Ministry of Skill Development and Entrepreneurship to promote apprenticeship training across the country by providing financial incentives to employers and direct stipend support to apprentices.",
    "description": "NAPS was launched by the Ministry of Skill Development and Entrepreneurship to promote apprenticeship training across the country by providing financial incentives to employers and direct stipend support to apprentices. It bridges the gap between formal education and industry requirements by incentivizing establishments to engage apprentices.",
    "eligibility": [
      "Candidates must be at least 14 years of age (18 years for hazardous industries) and meet minimum educational and physical fitness requirements for designated or optional trades (ITIs, graduates, diploma holders, 10th/12th pass). Employers registered with MCA/GSTN and having 30 or more employees are mandated, while smaller establishments can voluntarily participate."
    ],
    "benefits": [
      "Government reimburses 25% of prescribed stipend up to a maximum of Rs 1,500 per month per apprentice directly to the apprentice's bank account via DBT.",
      "Sharing of basic training cost up to Rs 7,500 per apprentice for non-ITI candidates with Basic Training Providers (BTP).",
      "Extensive on-the-job industrial experience and formal National Apprenticeship Certificate upon completion.",
      "Higher employability and industry-recognized qualifications."
    ],
    "documents": [
      "Aadhaar Card",
      "Educational qualification certificates (Class 10/12, ITI, Diploma, or Degree marksheet)",
      "Bank account details seeded with Aadhaar for DBT stipend transfers",
      "Passport size photograph"
    ],
    "howToApply": [
      "Apprentices register on the National Apprenticeship Portal (apprenticeshipindia.gov.in). Candidates search and apply for open apprenticeship opportunities posted by registered companies and accept contracts generated online."
    ],
    "whereToApply": "Apprentices register on the National Apprenticeship Portal (apprenticeshipindia.gov.in). Candidates search and apply for open apprenticeship opportuni",
    "conditions": [
      "Apprenticeship contracts must be generated and signed electronically through the portal.",
      "Candidates must not have previously undergone an apprenticeship training in the same trade.",
      "DBT stipend transfer is processed only to Aadhaar-seeded bank accounts."
    ],
    "source": {
      "label": "Apprenticeship India Portal (Directorate General of Training / MSDE)",
      "url": "https://www.apprenticeshipindia.gov.in/"
    }
  },
  {
    "slug": "national-health-mission",
    "name": "National Health Mission (NHM)",
    "category": "Healthcare",
    "image": "/images/categories/healthcare.svg",
    "summary": "National Health Mission (NHM) is an umbrella programme encompassing National Rural Health Mission (NRHM) and National Urban Health Mission (NUHM).",
    "description": "National Health Mission (NHM) is an umbrella programme encompassing National Rural Health Mission (NRHM) and National Urban Health Mission (NUHM). It aims to achieve universal access to equitable, affordable, and quality healthcare services for all, with a special focus on rural areas, the urban poor, women, children, and vulnerable population groups. NHM strengthens health systems, reduces maternal and child mortality, controls communicable diseases, and provides free essential medicines and diagnostics at public health facilities.",
    "eligibility": [
      "All citizens of India, with priority for rural and urban poor populations, pregnant women, children under 5, adolescent girls, persons from SC/ST and BPL families, and those with serious communicable diseases. Most NHM services are provided free of cost at government health facilities."
    ],
    "benefits": [
      "Free outpatient and inpatient services at government Primary Health Centres (PHCs), Community Health Centres (CHCs), District Hospitals, and Sub-Centres.",
      "Free essential medicines under the National Free Drugs Service Initiative.",
      "Free diagnostics at government health facilities under the National Free Diagnostics Service Initiative.",
      "Janani Suraksha Yojana (JSY): Cash incentive for institutional delivery — Rs 600–1,400 for rural areas, Rs 400–1,000 for urban areas depending on state category.",
      "Janani Shishu Suraksha Karyakram (JSSK): Free treatment for pregnant women and sick newborns at government hospitals including delivery, diagnostics, medicines, blood, diet, and referral transport.",
      "ASHA (Accredited Social Health Activist) workers available in every village as community health volunteers for guidance and referral.",
      "Rashtriya Bal Swasthya Karyakram (RBSK): Free health screening and treatment for children aged 0–18 years for 4 Ds — defects, deficiencies, diseases, and developmental delays.",
      "National Ambulance Service (108): Free emergency ambulance services."
    ],
    "documents": [
      "Aadhaar Card (for identity and DBT benefits like JSY)",
      "Mother and Child Protection (MCP) Card (for maternity and immunization benefits)",
      "BPL certificate (for priority services at some facilities)",
      "Bank account details for cash transfer benefits (JSY)"
    ],
    "howToApply": [
      "No formal application required. Citizens should visit their nearest Sub-Centre, Primary Health Centre, Community Health Centre, or District Hospital to avail NHM services. ASHA workers in rural areas can guide residents to appropriate health facilities and assist with entitlements under JSY and JSSK."
    ],
    "whereToApply": "No formal application required. Citizens should visit their nearest Sub-Centre, Primary Health Centre, Community Health Centre, or District Hospital t",
    "conditions": [
      "Services vary by state as NHM is implemented by respective State Health Societies with central funding.",
      "JSY cash incentive is paid after institutional delivery and is subject to registration and ANC visits.",
      "Free medicines and diagnostics are available at government facilities only — not applicable at private hospitals.",
      "ASHA worker performance incentives are outcome-based and not a salary."
    ],
    "source": {
      "label": "National Health Mission Portal",
      "url": "https://nhm.gov.in/"
    }
  },
  {
    "slug": "national-scholarship-portal",
    "name": "National Scholarship Portal (NSP) / Government Scholarship Schemes",
    "category": "Students",
    "image": "/images/categories/education.svg",
    "summary": "National Scholarship Portal (NSP) is a single, integrated digital portal created to provide end-to-end management of various scholarship schemes implemented by Central Ministries, State Governments, and Union Territories for pre-matric, post-matric, higher education, and merit-cum-means students.",
    "description": "National Scholarship Portal (NSP) is a single, integrated digital portal created to provide end-to-end management of various scholarship schemes implemented by Central Ministries, State Governments, and Union Territories for pre-matric, post-matric, higher education, and merit-cum-means students.",
    "eligibility": [
      "Students enrolled in recognized schools, colleges, universities, or technical/vocational institutions who fulfill the specific eligibility criteria (income limit, academic marks, category) of individual scholarship schemes hosted on NSP."
    ],
    "benefits": [
      "Single window interface for searching, applying, and tracking multiple Central and State scholarship schemes.",
      "Direct financial aid for tuition fees, maintenance allowances, hostel fees, and educational expenditures.",
      "Direct Benefit Transfer (DBT) directly into verified bank accounts of selected students."
    ],
    "documents": [
      "Aadhaar Card / OTR registration ID",
      "Educational marksheets of qualifying examination",
      "Income Certificate issued by competent state authority",
      "Category / Caste Certificate (SC/ST/OBC/EWS/Minority, if applicable)",
      "Domicile Certificate / Bonafide Student Certificate from institution",
      "Fee receipt of current academic year",
      "Active Aadhaar-seeded Bank Account details"
    ],
    "howToApply": [
      "Students register online on the NSP portal (scholarships.gov.in) using One-Time Registration (OTR) / Aadhaar, complete student verification, select eligible scholarship schemes, upload supporting documents, and submit applications for institutional and nodal officer verification."
    ],
    "whereToApply": "Students register online on the NSP portal (scholarships.gov.in) using One-Time Registration (OTR) / Aadhaar, complete student verification, select el",
    "conditions": [
      "A student can generally avail only one scholarship scheme hosted on NSP for a single course duration.",
      "Aadhaar-based e-KYC and institution verification are mandatory.",
      "Bank account must be seeded with Aadhaar for direct benefit disbursement."
    ],
    "source": {
      "label": "National Scholarship Portal",
      "url": "https://scholarships.gov.in/"
    }
  },
  {
    "slug": "nps-lite",
    "name": "National Pension System - Lite (NPS-Lite / Swavalamban)",
    "category": "Social Security",
    "image": "/images/categories/social.svg",
    "summary": "NPS-Lite was launched by the Pension Fund Regulatory and Development Authority (PFRDA) to cater specifically to economically disadvantaged individuals and groups in unorganised sectors who cannot afford high transaction fees.",
    "description": "NPS-Lite was launched by the Pension Fund Regulatory and Development Authority (PFRDA) to cater specifically to economically disadvantaged individuals and groups in unorganised sectors who cannot afford high transaction fees. Operating on a low-cost, group-based model through aggregators, it helps lower-income groups accumulate small savings systematically towards retirement.",
    "eligibility": [
      "Indian citizens aged between 18 and 60 years belonging to economically disadvantaged segments, unorganised sectors, or cooperative societies. Must not be covered under any social security or statutory retirement scheme such as EPF or government pension schemes."
    ],
    "benefits": [
      "Ultra-low administration and management fee structure designed specifically for low-income savers.",
      "Flexibility to make micro-contributions (minimum Rs 100 per contribution, with recommended minimum of Rs 1,000 per annum).",
      "Professional fund management by PFRDA-regulated pension fund managers (PFMs) investing in government securities and fixed income instruments.",
      "Lump sum withdrawal up to 60% of corpus at age 60, with the remaining 40% utilized to purchase an annuity providing a regular lifetime pension.",
      "Complete lump sum withdrawal permitted if the total accumulated corpus at age 60 is Rs 2 lakh or less."
    ],
    "documents": [
      "Aadhaar Card",
      "Identity and Address Proof (Voter ID, Ration Card, etc.)",
      "Bank account details (for electronic payout / ECS mandate)",
      "Passport size photograph"
    ],
    "howToApply": [
      "Enrollment is done through accredited aggregators such as Microfinance Institutions (MFIs), NGOs, NBFCs, banks, and state government bodies registered with PFRDA. The aggregator collects KYC documents, opens the PRAN (Permanent Retirement Account Number), and facilitates collection of contributions."
    ],
    "whereToApply": "Enrollment is done through accredited aggregators such as Microfinance Institutions (MFIs), NGOs, NBFCs, banks, and state government bodies registered",
    "conditions": [
      "NPS-Lite accounts are managed predominantly through accredited aggregator organizations.",
      "At least 40% of the accumulated corpus must be annuitized to provide monthly pension upon superannuation (unless total corpus is ≤ Rs 2,00,000).",
      "Premature exit before age 60 requires 80% of corpus to be annuitized."
    ],
    "source": {
      "label": "Pension Fund Regulatory and Development Authority (PFRDA) / NPS Trust",
      "url": "https://www.pfrda.org.in/"
    }
  },
  {
    "slug": "nsap",
    "name": "National Social Assistance Programme (NSAP)",
    "category": "Social Security",
    "image": "/images/categories/social.svg",
    "summary": "NSAP is a centrally sponsored scheme of the Ministry of Rural Development comprising five sub-schemes aimed at providing social security pensions and financial assistance to destitute elderly, widows, disabled persons, and bereaved BPL families.",
    "description": "NSAP is a centrally sponsored scheme of the Ministry of Rural Development comprising five sub-schemes aimed at providing social security pensions and financial assistance to destitute elderly, widows, disabled persons, and bereaved BPL families. The key components include Indira Gandhi National Old Age Pension Scheme (IGNOAPS), Indira Gandhi National Widow Pension Scheme (IGNWPS), Indira Gandhi National Disability Pension Scheme (IGNDPS), National Family Benefit Scheme (NFBS), and Annapurna.",
    "eligibility": [
      "Individuals belonging to households living Below Poverty Line (BPL) according to criteria prescribed by Government of India: For IGNOAPS: age 60 years and above. For IGNWPS: widows aged 40 to 79 years. For IGNDPS: persons aged 18 to 79 years with severe or multiple disabilities (80% disability or dwarfism). For NFBS: BPL household on death of primary breadwinner (aged 18-59 years)."
    ],
    "benefits": [
      "Old Age Pension (IGNOAPS): Monthly central assistance of Rs 200 per month for persons aged 60-79 years, and Rs 500 per month for persons aged 80 years and above (most state governments add top-ups of Rs 800 to Rs 2,500/month from state funds).",
      "Widow Pension (IGNWPS): Monthly central assistance of Rs 300 per month (aged 40-79) plus state top-ups.",
      "Disability Pension (IGNDPS): Monthly central assistance of Rs 300 per month (aged 18-79) plus state top-ups.",
      "National Family Benefit Scheme (NFBS): One-time lump sum grant of Rs 20,000 to the bereaved BPL household upon death of the primary breadwinner.",
      "Annapurna Scheme: 10 kg of food grains per month free of cost for eligible destitute senior citizens who remain uncovered under IGNOAPS."
    ],
    "documents": [
      "Aadhaar Card",
      "BPL Card / Ration Card demonstrating Below Poverty Line status",
      "Age proof certificate (birth certificate, voter ID, school certificate)",
      "Bank account passbook seeded with Aadhaar",
      "Disability certificate issued by Medical Board (for IGNDPS)",
      "Death certificate of husband (for IGNWPS) or breadwinner (for NFBS)"
    ],
    "howToApply": [
      "Applications on prescribed forms are submitted to the local Block Development Office (BDO), Sub-Divisional Magistrate (SDM), Municipal Corporation office, or through the state e-district / NSAP portal (nsap.nic.in). Verification is confirmed by Gram Panchayat / Urban local bodies."
    ],
    "whereToApply": "Applications on prescribed forms are submitted to the local Block Development Office (BDO), Sub-Divisional Magistrate (SDM), Municipal Corporation off",
    "conditions": [
      "BPL status verification is mandatory as per state guidelines and SECC/BPL lists.",
      "Beneficiaries must submit annual life certificates (Jeevan Pramaan) or undergo physical verification to continue receiving monthly pensions.",
      "Combined monthly payouts vary significantly by state due to varying supplementary state top-up amounts."
    ],
    "source": {
      "label": "National Social Assistance Programme (NSAP) Portal",
      "url": "https://nsap.nic.in/"
    }
  },
  {
    "slug": "one-stop-centre",
    "name": "One Stop Centre Scheme (Sakhi)",
    "category": "Women",
    "image": "/images/categories/women.svg",
    "summary": "The One Stop Centre (OSC) scheme, popularly known as 'Sakhi', is a centrally sponsored initiative under the Ministry of Women and Child Development.",
    "description": "The One Stop Centre (OSC) scheme, popularly known as 'Sakhi', is a centrally sponsored initiative under the Ministry of Women and Child Development. It facilitates access to an integrated range of services including medical aid, police assistance, legal aid/counseling, psycho-social counseling, and temporary shelter to women affected by violence, both in private and public spaces.",
    "eligibility": [
      "Any woman or girl facing violence, harassment, domestic abuse, sexual assault, dowry harassment, trafficking, or discrimination. Available to women irrespective of age, caste, religion, marital status, or socioeconomic background. Girls below 18 years of age are linked to relevant authorities under the POCSO Act and Juvenile Justice Act."
    ],
    "benefits": [
      "Immediate emergency rescue and medical assistance for women in distress.",
      "Assistance in filing First Information Report (FIR) or Non-Cognizable Report (NCR) through police facilitation desks.",
      "Psycho-social support and trauma counseling by professional counselors.",
      "Free legal aid, advice, and advocacy through empanelled lawyers or District Legal Services Authority (DLSA).",
      "Temporary shelter for up to 5 days with food, clothing, and basic necessities."
    ],
    "documents": [
      "No mandatory documentation required to access emergency aid or support services.",
      "Identity proof (Aadhaar Card, Voter ID, etc.) if available, but not a barrier for emergency care."
    ],
    "howToApply": [
      "Women can access a One Stop Centre directly by visiting the nearest Sakhi centre (typically located near district hospitals), calling the 181 Women Helpline, contacting the local police, or through referrals from NGOs, hospitals, or local authorities. No prior formal application is required."
    ],
    "whereToApply": "Women can access a One Stop Centre directly by visiting the nearest Sakhi centre (typically located near district hospitals), calling the 181 Women He",
    "conditions": [
      "Temporary shelter at the centre is strictly short-term (up to 5 days); longer-term shelter is arranged via Swadhar Greh or Ujjawala homes.",
      "Services are provided free of cost to any aggrieved woman.",
      "Minors are coordinated through Child Welfare Committees (CWC) in accordance with the law.",
      "Strict confidentiality of victim records and identity is maintained."
    ],
    "source": {
      "label": "Ministry of Women and Child Development (MWCD) / Sambal Sub-scheme under Mission Shakti",
      "url": "https://wcd.nic.in/"
    }
  },
  {
    "slug": "pm-care-for-children",
    "name": "PM CARES for Children Scheme",
    "category": "Social Security",
    "image": "/images/categories/social.svg",
    "summary": "Launched in May 2021 by the Prime Minister of India, the PM CARES for Children scheme supports children who lost both parents, legal guardian, adoptive parents, or surviving parent due to the COVID-19 pandemic.",
    "description": "Launched in May 2021 by the Prime Minister of India, the PM CARES for Children scheme supports children who lost both parents, legal guardian, adoptive parents, or surviving parent due to the COVID-19 pandemic. It ensures comprehensive care and protection through sustained health insurance, education, boarding support, and financial independence through a corpus of Rs 10 lakh upon reaching 23 years of age.",
    "eligibility": [
      "All children who lost both parents, surviving parent, or legal guardian/adoptive parents to the COVID-19 pandemic between 11 March 2020 and 28 February 2022, and had not completed 18 years of age at the time of parent's demise."
    ],
    "benefits": [
      "Corpus of Rs 10 lakh created in the child's name in a Post Office monthly income scheme, providing monthly stipend from age 18 to 23 for personal needs, and the entire lump-sum Rs 10 lakh handed over on completing 23 years of age.",
      "Free school education support: admission into nearest Kendriya Vidyalaya or private school with fees provided from PM CARES.",
      "Higher education support: assistance in obtaining education loans with interest paid by PM CARES, plus scholarship of Rs 20,000 per annum under Central Sector Scholarship.",
      "Health insurance coverage of Rs 5 lakh under PM-JAY (Ayushman Bharat) with premium paid by PM CARES until the age of 23 years.",
      "Child care institution (CCI) accommodation or foster care assistance."
    ],
    "documents": [
      "Death certificates of both parents mentioning COVID-19 or death during COVID period",
      "Birth certificate / age proof of the child",
      "Aadhaar Card of the child",
      "Joint bank/post office account with District Magistrate as guardian"
    ],
    "howToApply": [
      "Eligible children are identified and registered by District Magistrates (DM) on the pmcaresforchildren.in portal through Child Welfare Committees (CWC) and district child protection units."
    ],
    "whereToApply": "Eligible children are identified and registered by District Magistrates (DM) on the pmcaresforchildren.in portal through Child Welfare Committees (CWC",
    "conditions": [
      "Demise of parents must fall within the designated pandemic timeline window (March 2020 to February 2022).",
      "The District Magistrate acts as the legal guardian until the child attains 18 years of age.",
      "Monthly stipend from age 18 to 23 is funded through the interest accrued from the Rs 10 lakh corpus."
    ],
    "source": {
      "label": "PM CARES for Children Portal",
      "url": "https://pmcaresforchildren.in/"
    }
  },
  {
    "slug": "pm-fasal-bima-yojana",
    "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
    "category": "Farmers",
    "image": "/images/categories/agriculture.svg",
    "summary": "PMFBY is a crop insurance scheme launched in 2016 to provide financial support to farmers suffering crop loss or damage due to unforeseen events like natural calamities, pests, and diseases.",
    "description": "PMFBY is a crop insurance scheme launched in 2016 to provide financial support to farmers suffering crop loss or damage due to unforeseen events like natural calamities, pests, and diseases. It offers a uniform low-premium structure for farmers and ensures quick settlement of claims using technology such as remote sensing and crop cutting experiments.",
    "eligibility": [
      "All farmers growing notified crops in notified areas. Loanee farmers (those with Kisan Credit Card or seasonal agricultural operations loans) are covered compulsorily. Non-loanee farmers can enroll voluntarily. Sharecroppers and tenant farmers growing notified crops are also eligible."
    ],
    "benefits": [
      "Comprehensive risk coverage for pre-sowing, sowing, standing crop, post-harvest, and localized calamity risks.",
      "Low premium for farmers: 2% of sum insured for Kharif crops, 1.5% for Rabi crops, and 5% for annual commercial and horticultural crops.",
      "Balance premium paid by Central and State Governments in equal proportions (75:25 or 90:10 for NE and hilly states).",
      "Full sum insured payout for total crop loss based on yield data.",
      "Post-harvest losses covered for up to 14 days after harvest for crops left in cut and spread condition."
    ],
    "documents": [
      "Aadhaar Card",
      "Bank account passbook / account number",
      "Land records / Khasra Khatauni (for own land) or share-cropping agreement",
      "Sowing certificate from Patwari or Gram Panchayat",
      "Mobile number linked to Aadhaar"
    ],
    "howToApply": [
      "Loanee farmers are automatically enrolled through their bank (loan-linked). Non-loanee and voluntary farmers can apply through the PMFBY portal (pmfby.gov.in), CSC, nearest bank branch, or state agriculture department office. Deadline is the last date of enrolment for each crop season as notified by the state."
    ],
    "whereToApply": "Loanee farmers are automatically enrolled through their bank (loan-linked). Non-loanee and voluntary farmers can apply through the PMFBY portal (pmfby",
    "conditions": [
      "Coverage is limited to notified crops in notified areas each season — check state notification annually.",
      "Claim settlement uses area-based yield data from Crop Cutting Experiments (CCE); individual loss assessment is only for post-harvest and localized calamities.",
      "Non-loanee farmers must apply before the notified cut-off date for enrolment.",
      "Yield shortfall claims are settled after harvest season data is compiled; full payout is made when yield falls below threshold.",
      "The scheme excludes losses from war, nuclear risks, and willful negligence."
    ],
    "source": {
      "label": "PMFBY Portal",
      "url": "https://pmfby.gov.in/"
    }
  },
  {
    "slug": "pm-jan-vikas",
    "name": "Pradhan Mantri Jan Vikas Karyakram (PMJVK)",
    "category": "Social Security",
    "image": "/images/categories/social.svg",
    "summary": "PMJVK is a centrally sponsored scheme implemented by the Ministry of Minority Affairs (earlier known as Multi-sectoral Development Programme).",
    "description": "PMJVK is a centrally sponsored scheme implemented by the Ministry of Minority Affairs (earlier known as Multi-sectoral Development Programme). It is designed to address development deficits in identified Minority Concentration Areas (MCAs) by creating socio-economic infrastructure and basic amenities, with a primary focus on education, health, skill development, and women empowerment.",
    "eligibility": [
      "Targeted at populations residing in designated Minority Concentration Blocks (MCBs), Minority Concentration Towns (MCTs), and Minority Concentration District Headquarters (MCD HQs) identified based on minority population density and socio-economic/basic amenities backwardness. Open to all residents in these notified areas with special emphasis on minority communities."
    ],
    "benefits": [
      "Creation of high-standard educational infrastructure including residential schools, smart classrooms, hostels, IT labs, and Sadbhav Mandaps (community halls).",
      "Establishment of healthcare infrastructure: primary health centres (PHCs), community health centres (CHCs), maternal and child health wings, and diagnostic facilities.",
      "Skill development centres and industrial training institutes (ITIs) tailored to local livelihood opportunities.",
      "Special projects dedicated to women: working women hostels, girls' higher secondary schools, and vocational training facilities.",
      "At least 80% of resources earmarked for education, health, and skill development projects, and at least 33-40% specifically targeted for women and girls."
    ],
    "documents": [
      "Community facility access requires local area residence proof (Aadhaar, Ration card) or student enrollment records at beneficiary institutions."
    ],
    "howToApply": [
      "Proposals for community infrastructure projects are formulated by State Governments/UT administrations through District Level Committees (DLC) based on local gap analysis, and approved by the Empowered Committee of the Ministry of Minority Affairs. Individual community members access the physical facilities once built."
    ],
    "whereToApply": "Proposals for community infrastructure projects are formulated by State Governments/UT administrations through District Level Committees (DLC) based o",
    "conditions": [
      "PMJVK is an area development scheme rather than an individual cash transfer scheme.",
      "Projects are funded on a Centre-State cost sharing basis (typically 60:40 for general states, 90:10 for NE/Himalayan states, 100% for UTs without legislature).",
      "Land for project construction must be provided free of cost by the respective State Government."
    ],
    "source": {
      "label": "Ministry of Minority Affairs / PMJVK Portal",
      "url": "https://minorityaffairs.gov.in/"
    }
  },
  {
    "slug": "pm-kisan",
    "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
    "category": "Farmers",
    "image": "/images/categories/agriculture.svg",
    "summary": "PM-KISAN is a Central Sector Scheme providing income support to all landholding farmer families across the country to supplement their financial needs for procuring various inputs related to agriculture and allied activities as well as domestic needs.",
    "description": "PM-KISAN is a Central Sector Scheme providing income support to all landholding farmer families across the country to supplement their financial needs for procuring various inputs related to agriculture and allied activities as well as domestic needs.",
    "eligibility": [
      "All landholding farmer families who own cultivable land in their names, subject to specific exclusion criteria (e.g., institutional landholders, high-income individuals, serving or retired government employees, taxpayers)."
    ],
    "benefits": [
      "Financial benefit of ₹6,000 per year transferred directly into the bank accounts of beneficiary farmer families.",
      "Payable in three equal installments of ₹2,000 every four months."
    ],
    "documents": [
      "Aadhaar Card",
      "Proof of landownership / land holding documents",
      "Savings bank account details linked with Aadhaar",
      "Active mobile number"
    ],
    "howToApply": [
      "Farmers can self-register through the PM-KISAN web portal under 'Farmers Corner', via the PM-KISAN mobile app, or by visiting a local Common Service Centre (CSC) or state nodal officer."
    ],
    "whereToApply": "Farmers can self-register through the PM-KISAN web portal under 'Farmers Corner', via the PM-KISAN mobile app, or by visiting a local Common Service C",
    "conditions": [
      "e-KYC is mandatory for registered farmers to receive scheme installments.",
      "Bank accounts must be seeded with Aadhaar and enabled for Direct Benefit Transfer (DBT).",
      "Excludes institutional landholders, former/present constitutional post holders, ministers, MPs, MLAs, municipal corporation mayors, chairpersons of district panchayats, serving/retired government employees, retirees receiving monthly pension >= ₹10,000, persons who paid income tax in the last assessment year, and professionals like doctors, engineers, lawyers, and chartered accountants."
    ],
    "source": {
      "label": "PM-KISAN Portal",
      "url": "https://pmkisan.gov.in/"
    }
  },
  {
    "slug": "pm-krishi-sinchai-yojana",
    "name": "PM Krishi Sinchayee Yojana (PMKSY)",
    "category": "Farmers",
    "image": "/images/categories/agriculture.svg",
    "summary": "PMKSY aims to achieve the convergence of investments in irrigation at the field level, expand cultivable area under assured irrigation, improve on-farm water use efficiency to reduce wastage of water, enhance adoption of precision-irrigation and other water saving technologies (More Crop Per Drop), enhance recharge of aquifers, and introduce sustainable water conservation practices.",
    "description": "PMKSY aims to achieve the convergence of investments in irrigation at the field level, expand cultivable area under assured irrigation, improve on-farm water use efficiency to reduce wastage of water, enhance adoption of precision-irrigation and other water saving technologies (More Crop Per Drop), enhance recharge of aquifers, and introduce sustainable water conservation practices. Its slogan is 'Har Khet Ko Pani, More Crop Per Drop'.",
    "eligibility": [
      "All farmers with agricultural land are eligible for micro-irrigation subsidies under PMKSY-PDMC (Per Drop More Crop). Small and marginal farmers, women farmers, SC/ST farmers receive priority and higher subsidy percentages. States submit proposals under various components for irrigation infrastructure creation."
    ],
    "benefits": [
      "Micro-irrigation subsidy (drip and sprinkler irrigation systems): 55% subsidy for small and marginal farmers; 45% subsidy for other farmers on the cost of micro-irrigation equipment.",
      "Accelerated Irrigation Benefits Programme (AIBP): completion of long-pending major and medium irrigation projects for expanding irrigation potential.",
      "Har Khet Ko Pani: creation of new water sources, repair of existing water bodies, distribution network for assured water supply to every farm.",
      "Watershed development (WDC): development of rainfed areas through watershed management for soil and water conservation.",
      "Water savings of 30–50% with micro-irrigation leading to 40–100% increase in crop yield."
    ],
    "documents": [
      "Aadhaar Card",
      "Land ownership or tenancy records (Khasra/Khatauni)",
      "Bank account passbook",
      "Quotation from approved micro-irrigation vendor",
      "Photograph",
      "Category certificate (if SC/ST/small-marginal farmer)"
    ],
    "howToApply": [
      "Farmers apply for micro-irrigation subsidies through their State Agriculture or Horticulture Department or the State PMKSY Implementation Agency. Applications are submitted online through the state portal or at district agriculture offices. Equipment must be purchased from approved vendors listed by the state department."
    ],
    "whereToApply": "Farmers apply for micro-irrigation subsidies through their State Agriculture or Horticulture Department or the State PMKSY Implementation Agency. Appl",
    "conditions": [
      "Subsidy disbursement varies by state — contact the State Agriculture Department for current rates.",
      "Micro-irrigation installations must be from government-empanelled vendors to qualify for subsidy.",
      "Subsidy is provided directly to farmer's bank account via DBT after successful installation verification.",
      "The scheme has multiple components (AIBP, HKKP, WDC, PDMC) — farmers typically interact with the PDMC (micro-irrigation) component at the individual level."
    ],
    "source": {
      "label": "PMKSY Official Portal",
      "url": "https://pmksy.gov.in/"
    }
  },
  {
    "slug": "pm-matru-vandana-yojana",
    "name": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
    "category": "Women",
    "image": "/images/categories/women.svg",
    "summary": "PMMVY is a maternity benefit programme providing partial wage compensation to pregnant women and lactating mothers for the first time they have a child, and for the second child if it is a girl, to help them take adequate rest before and after delivery.",
    "description": "PMMVY is a maternity benefit programme providing partial wage compensation to pregnant women and lactating mothers for the first time they have a child, and for the second child if it is a girl, to help them take adequate rest before and after delivery. The scheme also promotes institutional delivery and provides cash incentives to improve maternal and child health and nutrition.",
    "eligibility": [
      "Pregnant Women and Lactating Mothers (PW&LM) for the first living child. For the second child: additional benefit if the second child is a girl. Women must be 19 years of age or above. Excludes central/state government employees who are already receiving maternity benefits under law."
    ],
    "benefits": [
      "Rs 5,000 in three installments for the first living child: Rs 1,000 on early registration of pregnancy, Rs 2,000 after 6 months of pregnancy on completion of at least one antenatal check-up, Rs 2,000 after child birth registration and completion of first cycle of child's vaccinations.",
      "For the second child (if a girl): Rs 6,000 in one installment after baby girl's birth registration and completion of full immunization.",
      "Beneficiaries also receive the cash incentive for institutional delivery under Janani Suraksha Yojana (JSY) — total effective benefit is Rs 6,000 or more."
    ],
    "documents": [
      "Mother and Child Protection (MCP) card",
      "Identity proof of beneficiary (Aadhaar Card)",
      "Bank account passbook (must be in the name of beneficiary)",
      "Mobile number",
      "Institutional delivery certificate (for 3rd installment)",
      "Child birth registration certificate (for 3rd installment)"
    ],
    "howToApply": [
      "Register at the nearest Anganwadi Centre (AWC) or Approved Health Facility (AHF). Applications can also be submitted online at pmmvy.wcd.gov.in (PMMVY-CAS portal). The Anganwadi Worker or ASHA worker can assist with registration. Documents must be submitted at each installment milestone."
    ],
    "whereToApply": "Register at the nearest Anganwadi Centre (AWC) or Approved Health Facility (AHF). Applications can also be submitted online at pmmvy.wcd.gov.in (PMMVY",
    "conditions": [
      "Benefits are available only for the first living child and, conditionally, the second child if she is a girl.",
      "Installment deadlines must be adhered to — benefits cannot be claimed retrospectively beyond the prescribed period.",
      "The Aadhaar-linked bank account must be in the beneficiary mother's name for direct benefit transfer.",
      "Central Government employees entitled to paid maternity leave are not eligible.",
      "Miscarriage or stillbirth: if a first delivery results in a child being stillborn, the woman is eligible for fresh benefits in the next pregnancy."
    ],
    "source": {
      "label": "PMMVY Official Portal",
      "url": "https://pmmvy.wcd.gov.in/"
    }
  },
  {
    "slug": "pm-poshan",
    "name": "PM POSHAN (Pradhan Mantri Poshan Shakti Nirman) – Mid-Day Meal Scheme",
    "category": "Students",
    "image": "/images/categories/education.svg",
    "summary": "PM POSHAN (formerly Mid-Day Meal Scheme) is the world's largest school meal programme providing free, hot, nutritious mid-day meals to students in government and government-aided primary and upper primary schools (Classes 1–8).",
    "description": "PM POSHAN (formerly Mid-Day Meal Scheme) is the world's largest school meal programme providing free, hot, nutritious mid-day meals to students in government and government-aided primary and upper primary schools (Classes 1–8). The scheme aims to improve the nutritional status of school children, increase school enrollment, reduce drop-out rates, address classroom hunger, and boost attendance — particularly among girls, SC/ST, and disadvantaged communities.",
    "eligibility": [
      "All students enrolled in Classes 1–8 (Primary and Upper Primary) in government, government-aided, and local body schools, as well as Anganwadi Centres for classes under the scheme. Students in Madrasa and Maktabs supported by the Minority Affairs Ministry are also covered. No income or caste restriction — the meal is available to all enrolled students."
    ],
    "benefits": [
      "Free, hot, nutritious cooked mid-day meal served on all school days (approximately 200 days per year).",
      "Caloric and protein entitlements: Primary students (Classes 1–5): 700 Kcal, 20g protein per meal; Upper Primary (Classes 6–8): 1,046 Kcal, 28g protein per meal.",
      "All ingredients including cereals, pulses, vegetables, oil, condiments, and fuel costs are covered by the scheme.",
      "Special meals during school events, local festivals, and special occasions.",
      "Nutritional fortification and local produce integration encouraged."
    ],
    "documents": [
      "No documents required — automatically available to all enrolled students in eligible schools"
    ],
    "howToApply": [
      "No application needed. Students in eligible government schools automatically receive mid-day meals on all school days. Parents and guardians should ensure their children are enrolled in government schools to benefit. For concerns or complaints, contact the School Management Committee (SMC) or local Block Education Officer."
    ],
    "whereToApply": "No application needed. Students in eligible government schools automatically receive mid-day meals on all school days. Parents and guardians should en",
    "conditions": [
      "Meals are provided on school days only — no take-home rations under this scheme.",
      "The scheme covers Classes 1–8 only; pre-primary (Anganwadi) nutrition is handled under ICDS/POSHAN Abhiyan.",
      "Quality monitoring is conducted through School Management Committees and district-level inspections.",
      "Private unaided schools are not covered under this scheme."
    ],
    "source": {
      "label": "PM POSHAN Portal",
      "url": "https://pmposhan.education.gov.in/"
    }
  },
  {
    "slug": "pm-svanidhi",
    "name": "PM Street Vendor's AtmaNirbhar Nidhi (PM SVANidhi)",
    "category": "Housing",
    "image": "/images/categories/housing.svg",
    "summary": "PM SVANidhi is a Special Micro-Credit Facility launched to provide affordable working capital loans to street vendors affected by the COVID-19 pandemic, enabling them to resume their livelihoods and transition into the formal financial system.",
    "description": "PM SVANidhi is a Special Micro-Credit Facility launched to provide affordable working capital loans to street vendors affected by the COVID-19 pandemic, enabling them to resume their livelihoods and transition into the formal financial system.",
    "eligibility": [
      "Urban street vendors engaged in vending in urban areas on or before March 24, 2020, possessing a Certificate of Vending / Identity Card, or identified in urban local body (ULB) surveys, or recommendation letter from ULB/TVC."
    ],
    "benefits": [
      "Initial working capital loan up to ₹10,000 with a 1-year tenure.",
      "Second tranche loan up to ₹20,000 on timely repayment of the first loan.",
      "Third tranche loan up to ₹50,000 on timely repayment of the second loan.",
      "Interest subsidy of 7% per annum credited to beneficiary bank accounts quarterly.",
      "Cashback incentive up to ₹1,200 per annum for performing digital transaction transitions."
    ],
    "documents": [
      "Aadhaar Card",
      "Voter ID / Driving License / Ration Card",
      "Certificate of Vending / ID Card issued by Urban Local Body (ULB) or Letter of Recommendation (LoR)",
      "Bank Account passbook / details",
      "Active mobile number linked with Aadhaar"
    ],
    "howToApply": [
      "Street vendors can apply online via the PM SVANidhi portal (pmsvanidhi.mohua.gov.in) or mobile app with assistance from Common Service Centres (CSCs), ULB officials, or lending institution branches."
    ],
    "whereToApply": "Street vendors can apply online via the PM SVANidhi portal (pmsvanidhi.mohua.gov.in) or mobile app with assistance from Common Service Centres (CSCs),",
    "conditions": [
      "No collateral is required for loans under this scheme.",
      "Interest subsidy applies to timely or early repayment.",
      "Digital transaction performance unlocks monthly cashback benefits directly into the vendor's account."
    ],
    "source": {
      "label": "PM SVANidhi Portal",
      "url": "https://pmsvanidhi.mohua.gov.in/"
    }
  },
  {
    "slug": "pm-sym",
    "name": "Pradhan Mantri Shram Yogi Maan-dhan (PM-SYM)",
    "category": "Social Security",
    "image": "/images/categories/social.svg",
    "summary": "PM-SYM is a central sector pension scheme administered by the Ministry of Labour and Employment and implemented through the Life Insurance Corporation of India (LIC) and CSC e-Governance Services.",
    "description": "PM-SYM is a central sector pension scheme administered by the Ministry of Labour and Employment and implemented through the Life Insurance Corporation of India (LIC) and CSC e-Governance Services. It is designed to provide old-age income security to unorganised workers whose monthly income is Rs 15,000 or less.",
    "eligibility": [
      "Unorganised workers (such as street vendors, agricultural workers, construction workers, domestic helpers, rickshaw pullers, rag pickers, handloom workers) aged between 18 and 40 years. Monthly income must be Rs 15,000 or below. Should NOT be covered under EPFO, ESIC, or NPS (government-funded) and must not be an income tax payer."
    ],
    "benefits": [
      "Assured minimum monthly pension of Rs 3,000 after attaining the age of 60 years.",
      "50% matching contribution by the Central Government: beneficiary contributes Rs 55 to Rs 200 per month depending on entry age, and the Government deposits an equal matching amount.",
      "Spousal family pension: in case of death of the subscriber during pension receipt, spouse receives 50% of the pension amount (Rs 1,500/month).",
      "Option for spouse to continue the scheme by paying regular contributions if the subscriber dies before age 60."
    ],
    "documents": [
      "Aadhaar Card",
      "Savings bank account passbook / Jan Dhan account details with IFSC",
      "Active mobile number"
    ],
    "howToApply": [
      "Eligible unorganised workers can visit any Common Services Centre (CSC) with their Aadhaar card and bank passbook. The Village Level Entrepreneur (VLE) completes the digital registration, initial contribution is paid in cash, and subsequent contributions are auto-debited monthly from the subscriber's bank account. Alternatively, workers can self-enroll via maandhan.in."
    ],
    "whereToApply": "Eligible unorganised workers can visit any Common Services Centre (CSC) with their Aadhaar card and bank passbook. The Village Level Entrepreneur (VLE",
    "conditions": [
      "Subscriber must maintain sufficient balance in the savings account for auto-debit; missed contributions attract late fees.",
      "If subscriber exits before 10 years, only subscriber's share of contribution with savings bank interest rate is returned.",
      "Income tax payers and organized sector employees covered under EPF/ESIC are strictly ineligible."
    ],
    "source": {
      "label": "Maan-dhan Portal / Ministry of Labour and Employment",
      "url": "https://maandhan.in/"
    }
  },
  {
    "slug": "pm-ujjwala-yojana",
    "name": "Pradhan Mantri Ujjwala Yojana (PMUY / Ujjwala 2.0)",
    "category": "Women",
    "image": "/images/categories/women.svg",
    "summary": "Pradhan Mantri Ujjwala Yojana aims to provide clean cooking fuel (LPG) to deposit-free connections for women from low-income households, reducing health hazards associated with traditional cooking fuels.",
    "description": "Pradhan Mantri Ujjwala Yojana aims to provide clean cooking fuel (LPG) to deposit-free connections for women from low-income households, reducing health hazards associated with traditional cooking fuels.",
    "eligibility": [
      "Adult women belonging to poor households (SC/ST, Pradhan Mantri Awas Yojana, Antyodaya Anna Yojana, Most Backward Classes, Tea & Ex-Tea Garden Tribes, Forest Dwellers, Islands/River Islands, or 14-point declaration poor households) having no existing LPG connection in the household."
    ],
    "benefits": [
      "Deposit-free LPG connection including a pressure regulator, safety hose, LPG booklet, and domestic gas cylinder.",
      "Financial support of ₹1,600 per connection provided by the Central Government.",
      "First LPG refill and hotplate (stove) provided free of cost to the beneficiary.",
      "Targeted government subsidy per 14.2 kg cylinder for specified refills."
    ],
    "documents": [
      "Know Your Customer (KYC) form",
      "Aadhaar Card of the applicant woman and adult family members listed in Ration Card",
      "Ration Card / family composition document issued by State Government",
      "Bank Account number and IFSC code of the applicant",
      "Proof of address (Aadhaar Card, Utility Bill)"
    ],
    "howToApply": [
      "Applicants can apply online via the official PMUY portal (pmuy.gov.in) or by submitting an application form directly to the nearest LPG distributor of IOCL, BPCL, or HPCL."
    ],
    "whereToApply": "Applicants can apply online via the official PMUY portal (pmuy.gov.in) or by submitting an application form directly to the nearest LPG distributor of",
    "conditions": [
      "Applicant must be an adult woman (at least 18 years old).",
      "There must not be any existing LPG connection in the same household.",
      "Under Ujjwala 2.0, migrant workers can submit a self-declaration in place of proof of address and ration card."
    ],
    "source": {
      "label": "PMUY Official Website",
      "url": "https://www.pmuy.gov.in/"
    }
  },
  {
    "slug": "pm-vishwakarma",
    "name": "PM Vishwakarma Scheme",
    "category": "Employment",
    "image": "/images/categories/employment.svg",
    "summary": "PM Vishwakarma is a Central Sector Scheme launched to provide holistic end-to-end support to traditional artisans and craftspeople ('Vishwakarmas') who work with their hands and tools, enhancing their product quality, market reach, and economic standing.",
    "description": "PM Vishwakarma is a Central Sector Scheme launched to provide holistic end-to-end support to traditional artisans and craftspeople ('Vishwakarmas') who work with their hands and tools, enhancing their product quality, market reach, and economic standing.",
    "eligibility": [
      "Artisans or craftspeople working with hands and tools in one of the 18 covered traditional trades (e.g., Carpenter, Boat Maker, Armourer, Blacksmith, Locksmith, Goldsmith, Potter, Sculptor, Cobbler, Mason, Basket/Mat/Broom Maker, Doll & Toy Maker, Barber, Garland Maker, Washerman, Tailor, Fishing Net Maker). Minimum age of beneficiary is 18 years. Limited to one member per family."
    ],
    "benefits": [
      "Recognition: PM Vishwakarma Certificate and ID Card.",
      "Skill Upgradation: Basic training of 5-7 days and Advanced training of 15 days or more, with a stipend of ₹500 per day.",
      "Toolkit Incentive: Digital e-voucher of up to ₹15,000 for purchasing modern tools.",
      "Credit Support: Collateral-free enterprise development loan of up to ₹1,00,000 (1st tranche) and up to ₹2,00,000 (2nd tranche) at a concessional interest rate of 5%.",
      "Incentive for Digital Transactions: ₹1 per digital transaction for up to 100 transactions monthly.",
      "Marketing Support: Quality certification, branding, e-commerce onboarding, and trade fair linkage."
    ],
    "documents": [
      "Aadhaar Card",
      "Active Mobile Number",
      "Bank Account details (Aadhaar linked)",
      "Ration Card (for family verification)"
    ],
    "howToApply": [
      "Artisans can register online through the PM Vishwakarma Portal (pmvishwakarma.gov.in) at nearest Common Service Centres (CSCs), followed by a 3-stage verification process (Gram Panchayat/ULB level, District Implementation Committee level, and Screening Committee level)."
    ],
    "whereToApply": "Artisans can register online through the PM Vishwakarma Portal (pmvishwakarma.gov.in) at nearest Common Service Centres (CSCs), followed by a 3-stage ",
    "conditions": [
      "Beneficiary should be engaged in the trade concerned on the date of registration.",
      "Only one member of the family (husband, wife, and unmarried children) is eligible to get benefits under the scheme.",
      "Beneficiary should not have availed loans under similar credit-based schemes (e.g., PMEGP, PM SVANidhi, MUDRA) in the last 5 years."
    ],
    "source": {
      "label": "PM Vishwakarma Official Portal",
      "url": "https://pmvishwakarma.gov.in/"
    }
  },
  {
    "slug": "pm-yasasvi",
    "name": "PM Young Achievers Scholarship Award Scheme for Vibrant India (PM YASASVI)",
    "category": "Students",
    "image": "/images/categories/education.svg",
    "summary": "PM YASASVI is a Central Sector Scheme providing top-class education scholarships and financial assistance to meritorious students belonging to OBC, EBC, and DNT categories to pursue secondary and higher education.",
    "description": "PM YASASVI is a Central Sector Scheme providing top-class education scholarships and financial assistance to meritorious students belonging to OBC, EBC, and DNT categories to pursue secondary and higher education.",
    "eligibility": [
      "Students belonging to Other Backward Classes (OBC), Economically Backward Classes (EBC), and Denotified, Nomadic & Semi-Nomadic Tribes (DNT) whose parental/family annual income from all sources does not exceed ₹2.5 lakh per annum, studying in identified Top Class Schools or Colleges."
    ],
    "benefits": [
      "Top Class School Education: Scholarship up to ₹75,000 per annum for Class 9 and 10, and up to ₹1,25,000 per annum for Class 11 and 12, covering tuition fees and hostel fees.",
      "Top Class College Education: Full tuition fee reimbursement up to prescribed limits along with living allowance, book allowance, and computer hardware grant for students in designated top institutions.",
      "Funds disbursed directly via Direct Benefit Transfer (DBT) into bank accounts."
    ],
    "documents": [
      "Aadhaar Card",
      "OBC / EBC / DNT Category Certificate issued by competent authority",
      "Income Certificate showing annual family income up to ₹2.5 lakh",
      "Marksheet of previous qualifying class",
      "Bonafide Student Certificate / Admission proof from school or college",
      "Active Aadhaar-seeded Bank Account details"
    ],
    "howToApply": [
      "Eligible students must apply online via the National Scholarship Portal (NSP) at scholarships.gov.in during the designated application period."
    ],
    "whereToApply": "Eligible students must apply online via the National Scholarship Portal (NSP) at scholarships.gov.in during the designated application period.",
    "conditions": [
      "Students must belong to OBC, EBC, or DNT categories with family annual income <= ₹2.5 lakh.",
      "Selection for top class school/college scholarships is based on merit criteria as notified on the National Scholarship Portal.",
      "Institutional verification on NSP is mandatory for scheme processing."
    ],
    "source": {
      "label": "National Scholarship Portal / AICTE PM YASASVI Portal",
      "url": "https://yashasvi.aicte.gov.in/"
    }
  },
  {
    "slug": "pmay-gramin",
    "name": "Pradhan Mantri Awaas Yojana - Gramin (PMAY-G)",
    "category": "Farmers",
    "image": "/images/categories/agriculture.svg",
    "summary": "PMAY-G (formerly Indira Awaas Yojana) was revamped in 2016 by the Ministry of Rural Development with the objective of providing 'Housing for All' in rural areas.",
    "description": "PMAY-G (formerly Indira Awaas Yojana) was revamped in 2016 by the Ministry of Rural Development with the objective of providing 'Housing for All' in rural areas. It provides direct financial assistance to rural houseless households and those living in kutcha and dilapidated houses for construction of pucca houses equipped with basic amenities.",
    "eligibility": [
      "Rural households with no home (houseless) or living in kutcha houses with zero, one, or two rooms, identified and prioritized using the Socio-Economic and Caste Census (SECC 2011) deprivation parameters and finalized through Gram Sabha verification (Awaas+ survey list). Households owning motorized vehicles, agricultural equipment, or salaried members are excluded."
    ],
    "benefits": [
      "Financial unit assistance of Rs 1,20,000 in plain areas and Rs 1,30,000 in hilly, difficult, and Integrated Action Plan (IAP) districts.",
      "Additional assistance of up to Rs 12,000 for toilet construction through convergence with Swachh Bharat Mission - Gramin (SBM-G).",
      "90 to 95 person-days of unskilled labor support under MGNREGA (approx Rs 18,000–Rs 25,000 depending on state wage rates).",
      "Convergence for electricity connection (Saubhagya), clean cooking LPG connection (PM Ujjwala Yojana), and piped drinking water (Jal Jeevan Mission).",
      "Minimum house size of 25 square meters including a dedicated cooking area."
    ],
    "documents": [
      "Aadhaar Card of beneficiary and spouse",
      "Bank account passbook seeded with Aadhaar and NPCI mapper",
      "Consent form for Aadhaar authentication",
      "MGNREGA Job Card number",
      "Land ownership document / certificate of land allotment"
    ],
    "howToApply": [
      "Beneficiaries are identified systematically through the SECC 2011 and verified Awaas+ list by the Gram Panchayat. Direct benefit transfer (DBT) installments are disbursed directly to the beneficiary's bank account linked to Aadhaar across 3-4 construction stages (foundation, lintel, roof, and completion), tracked via geo-tagged photos on the AwaasApp."
    ],
    "whereToApply": "Beneficiaries are identified systematically through the SECC 2011 and verified Awaas+ list by the Gram Panchayat. Direct benefit transfer (DBT) instal",
    "conditions": [
      "Assistance is transferred in progressive installments based strictly on geo-tagged photo verification of construction milestones via AwaasApp.",
      "House ownership is registered jointly in the name of husband and wife, or exclusively in the name of the female head of the family.",
      "Contractors or middlemen are prohibited from building the house; construction must be carried out by the beneficiary."
    ],
    "source": {
      "label": "Pradhan Mantri Awaas Yojana - Gramin Portal (PMAY-G / AwaasSoft)",
      "url": "https://pmayg.nic.in/"
    }
  },
  {
    "slug": "pmay-urban",
    "name": "Pradhan Mantri Awas Yojana – Urban (PMAY-U / PMAY-U 2.0)",
    "category": "Housing",
    "image": "/images/categories/housing.svg",
    "summary": "Pradhan Mantri Awas Yojana – Urban aims to address urban housing shortage among Economically Weaker Section (EWS), Low Income Group (LIG), and Middle Income Group (MIG) categories by providing all-weather pucca houses with basic civic amenities.",
    "description": "Pradhan Mantri Awas Yojana – Urban aims to address urban housing shortage among Economically Weaker Section (EWS), Low Income Group (LIG), and Middle Income Group (MIG) categories by providing all-weather pucca houses with basic civic amenities.",
    "eligibility": [
      "Urban families belonging to EWS, LIG, or MIG categories who do not own a pucca house in their name or any family member's name anywhere in India."
    ],
    "benefits": [
      "Financial assistance and interest subsidy for construction, enhancement, or purchase of houses across various verticals:",
      "In-situ Slum Redevelopment (ISSR)",
      "Credit Linked Subsidy Scheme (CLSS) / Interest Subsidy Scheme (ISS)",
      "Affordable Housing in Partnership (AHP)",
      "Beneficiary-led Individual House Construction / Enhancement (BLC)"
    ],
    "documents": [
      "Aadhaar Card of all family members",
      "Proof of income (Income Certificate, Salary Slips, Form 16, Bank statements)",
      "Proof of identity and residential address",
      "Land ownership documents / land record details (for BLC component)",
      "Affidavit/undertaking stating the family does not own a pucca house in India",
      "Active bank account details linked with Aadhaar"
    ],
    "howToApply": [
      "Eligible urban residents can apply online through the PMAY-Urban portal (pmay-urban.gov.in), mobile app, via designated Common Service Centres (CSCs), or through local Urban Local Bodies (ULBs)."
    ],
    "whereToApply": "Eligible urban residents can apply online through the PMAY-Urban portal (pmay-urban.gov.in), mobile app, via designated Common Service Centres (CSCs),",
    "conditions": [
      "Beneficiary family must not own a pucca house in any part of India.",
      "House ownership or co-ownership must be mandated in the name of female head of household or joint ownership with spouse (in EWS/LIG categories).",
      "Carpet area limitations apply based on the specific income category guidelines."
    ],
    "source": {
      "label": "PMAY-Urban Portal",
      "url": "https://pmay-urban.gov.in/"
    }
  },
  {
    "slug": "pmegp",
    "name": "Prime Minister's Employment Generation Programme (PMEGP)",
    "category": "Employment",
    "image": "/images/categories/employment.svg",
    "summary": "PMEGP is a flagship credit-linked subsidy programme administered by the Ministry of Micro, Small and Medium Enterprises (MSME) and implemented by Khadi and Village Industries Commission (KVIC) at the national level.",
    "description": "PMEGP is a flagship credit-linked subsidy programme administered by the Ministry of Micro, Small and Medium Enterprises (MSME) and implemented by Khadi and Village Industries Commission (KVIC) at the national level. It facilitates generation of employment opportunities through the establishment of micro-enterprises in non-farm sectors across rural and urban India.",
    "eligibility": [
      "Any individual above 18 years of age. For manufacturing projects costing above Rs 10 lakh and service projects costing above Rs 5 lakh, minimum educational qualification of Class 8 pass is required. Self-Help Groups (SHGs), production-based co-operative societies, and charitable trusts are also eligible. Existing units or units already availing government subsidies under other schemes are ineligible."
    ],
    "benefits": [
      "Margin money (subsidy) up to 25% of project cost in urban areas and up to 35% in rural areas for special categories (SC/ST/OBC/Women/Ex-servicemen/PH/NER/Hill areas).",
      "General category receives 15% subsidy in urban areas and 25% in rural areas.",
      "Maximum admissible project cost is Rs 50 lakh for manufacturing sector and Rs 20 lakh for service/business sector.",
      "Beneficiary contribution is only 5% of project cost for special categories (10% for general category).",
      "Second loan of up to Rs 1 crore for manufacturing (Rs 25 lakh for service) available for existing well-performing PMEGP units for expansion."
    ],
    "documents": [
      "Aadhaar Card and PAN Card",
      "Detailed Project Report (DPR)",
      "Educational qualification certificate (Class 8 or higher)",
      "Caste / Category certificate (for SC/ST/OBC/minority subsidy claims)",
      "Rural area certificate (issued by competent local authority if applying under rural quota)",
      "EDP (Entrepreneurship Development Programme) training certificate before loan disbursement"
    ],
    "howToApply": [
      "Apply online through the PMEGP e-Portal on kviconline.gov.in. Applications are processed by District Industries Centres (DIC) or KVIC/KVIB offices and forwarded to partner financing banks for sanction."
    ],
    "whereToApply": "Apply online through the PMEGP e-Portal on kviconline.gov.in. Applications are processed by District Industries Centres (DIC) or KVIC/KVIB offices and",
    "conditions": [
      "Subsidy is credited as Margin Money in an escrow account and locked for 3 years, after which physical verification determines final adjustment against loan principal.",
      "Only new micro-enterprises are eligible for the first-time subsidy.",
      "Mandatory EDP training (can be completed online or offline) is required before bank loan disbursement."
    ],
    "source": {
      "label": "PMEGP e-Portal / Khadi and Village Industries Commission",
      "url": "https://www.kviconline.gov.in/pmegpeportal/"
    }
  },
  {
    "slug": "pmjdy",
    "name": "Pradhan Mantri Jan-Dhan Yojana (PMJDY)",
    "category": "Financial Support",
    "image": "/images/categories/financial.svg",
    "summary": "Pradhan Mantri Jan-Dhan Yojana is the National Mission for Financial Inclusion launched to provide universal access to banking services, basic savings accounts, remittance options, credit, insurance, and pension to unbanked households.",
    "description": "Pradhan Mantri Jan-Dhan Yojana is the National Mission for Financial Inclusion launched to provide universal access to banking services, basic savings accounts, remittance options, credit, insurance, and pension to unbanked households.",
    "eligibility": [
      "Any Indian citizen aged 10 years and above who does not hold a basic bank account can open a PMJDY account."
    ],
    "benefits": [
      "Zero-balance basic savings bank deposit (BSBD) account with no minimum balance requirement.",
      "Interest earned on deposits in the PMJDY account.",
      "Issuance of RuPay Debit Card with built-in accidental insurance cover up to ₹2,00,000 (for accounts opened after August 28, 2018).",
      "Overdraft (OD) facility up to ₹10,000 for eligible account holders after 6 months of satisfactory operation.",
      "Direct Benefit Transfer (DBT) of government welfare subsidies into the account."
    ],
    "documents": [
      "Aadhaar Card (or officially valid documents: Voter ID, Driving License, PAN Card, Passport, NREGA Job Card)",
      "Passport-size photograph",
      "Self-declaration / proof of identity if official documents are unavailable (Small Account provision)"
    ],
    "howToApply": [
      "Interested individuals can visit any bank branch, Bank Mitra / Business Correspondent location, or designated financial center to fill out the PMJDY account opening form."
    ],
    "whereToApply": "Interested individuals can visit any bank branch, Bank Mitra / Business Correspondent location, or designated financial center to fill out the PMJDY a",
    "conditions": [
      "RuPay Card accidental insurance is valid only if the card has been used at least once for a successful financial or non-financial transaction within 90 days prior to the accident.",
      "Overdraft limit of up to ₹10,000 is subject to bank evaluation and account operational history."
    ],
    "source": {
      "label": "PMJDY Official Portal",
      "url": "https://pmjdy.gov.in/"
    }
  },
  {
    "slug": "pmkvy",
    "name": "Pradhan Mantri Kaushal Vikas Yojana (PMKVY)",
    "category": "Employment",
    "image": "/images/categories/employment.svg",
    "summary": "PMKVY is the flagship outcome-based skill training scheme of the Ministry of Skill Development and Entrepreneurship (MSDE), implemented by the National Skill Development Corporation (NSDC).",
    "description": "PMKVY is the flagship outcome-based skill training scheme of the Ministry of Skill Development and Entrepreneurship (MSDE), implemented by the National Skill Development Corporation (NSDC). It aims to enable Indian youth to take up industry-relevant skill training that helps them secure a better livelihood, offering Short Term Training (STT) and Recognition of Prior Learning (RPL).",
    "eligibility": [
      "Indian nationals who are school/college dropouts or unemployed youth aged between 15 and 45 years. Possess valid Aadhaar and bank account. For Recognition of Prior Learning (RPL), individuals with prior informal learning or work experience in relevant sectors are eligible."
    ],
    "benefits": [
      "Free skill certification and training across hundreds of National Skills Qualifications Framework (NSQF) aligned job roles.",
      "Training and assessment fees completely borne by the Government.",
      "Accredited certification jointly issued by Skill India, Sector Skill Councils, and NSDC.",
      "Placement assistance and career counseling following course completion for Short Term Training candidates.",
      "Monetary reward / reward voucher upon successful certification under specified RPL components."
    ],
    "documents": [
      "Aadhaar Card",
      "Bank account details (account number, IFSC code)",
      "Educational certificates / highest qualification marksheet (if applicable)",
      "Passport size photographs"
    ],
    "howToApply": [
      "Candidates register online at the Skill India Digital portal (skillindiadigital.gov.in) or visit their nearest Pradhan Mantri Kaushal Kendra (PMKK) or accredited training centre. Candidates choose a sector and training job role, undergo training, and appear for standardized third-party assessment."
    ],
    "whereToApply": "Candidates register online at the Skill India Digital portal (skillindiadigital.gov.in) or visit their nearest Pradhan Mantri Kaushal Kendra (PMKK) or",
    "conditions": [
      "A candidate can undergo subsidized training only once under STT unless undertaking an authorized advanced level upskilling course.",
      "Attendance must meet the minimum threshold (typically 70-80%) verified through biometric Aadhaar-enabled attendance systems.",
      "Certification is strictly issued after clearing the formal assessment by an independent assessment agency."
    ],
    "source": {
      "label": "Pradhan Mantri Kaushal Vikas Yojana / Skill India Digital",
      "url": "https://www.pmkvyofficial.org/"
    }
  },
  {
    "slug": "pmsby",
    "name": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
    "category": "Social Security",
    "image": "/images/categories/social.svg",
    "summary": "Pradhan Mantri Suraksha Bima Yojana is a government-sponsored annual accidental death and disability insurance scheme providing coverage against accidental death or permanent disability.",
    "description": "Pradhan Mantri Suraksha Bima Yojana is a government-sponsored annual accidental death and disability insurance scheme providing coverage against accidental death or permanent disability.",
    "eligibility": [
      "Indian citizens aged between 18 and 70 years having an active savings bank account or post office account who give auto-debit consent for the annual premium."
    ],
    "benefits": [
      "Accidental death coverage of ₹2,00,000.",
      "Total and irrecoverable loss of both eyes or loss of use of both hands or feet or loss of sight of one eye and loss of use of hand or foot coverage of ₹2,00,000.",
      "Total and irrecoverable loss of sight of one eye or loss of use of one hand or foot coverage of ₹1,00,000.",
      "Extremely low annual premium of ₹20 per annum (revised from ₹12)."
    ],
    "documents": [
      "Savings Bank Account / Post Office Account details",
      "Aadhaar Card",
      "Nominee details",
      "Auto-debit consent authorization"
    ],
    "howToApply": [
      "Eligible bank/post office account holders can enroll by submitting the auto-debit consent form at their bank branch or activating it via netbanking / mobile banking app."
    ],
    "whereToApply": "Eligible bank/post office account holders can enroll by submitting the auto-debit consent form at their bank branch or activating it via netbanking / ",
    "conditions": [
      "Annual premium of ₹20 is auto-debited from the subscriber's bank account every year before May 31.",
      "Coverage period is from June 1 to May 31 of the succeeding year.",
      "Cover terminates if the subscriber turns 70, closes the bank account, or maintains insufficient account balance for premium debit."
    ],
    "source": {
      "label": "Department of Financial Services, Ministry of Finance",
      "url": "https://financialservices.gov.in/pradhan-mantri-suraksha-bima-yojana-pmsby"
    }
  },
  {
    "slug": "post-matric-scholarship",
    "name": "Post-Matric Scholarship for SC, ST, OBC Students",
    "category": "Students",
    "image": "/images/categories/education.svg",
    "summary": "Post-Matric Scholarships are Central Sector Scholarships provided by the Ministry of Social Justice & Empowerment (for SC and OBC students) and the Ministry of Tribal Affairs (for ST students) to support students from Scheduled Castes, Scheduled Tribes, and Other Backward Classes to complete their education from Class 11 onwards up to PhD level, including professional and technical courses.",
    "description": "Post-Matric Scholarships are Central Sector Scholarships provided by the Ministry of Social Justice & Empowerment (for SC and OBC students) and the Ministry of Tribal Affairs (for ST students) to support students from Scheduled Castes, Scheduled Tribes, and Other Backward Classes to complete their education from Class 11 onwards up to PhD level, including professional and technical courses. The scheme enables poor students from marginalized communities to pursue higher education without financial barriers.",
    "eligibility": [
      "For SC/OBC: Students from Scheduled Castes or OBC communities studying in Class 11 and above (including degree, postgraduate, diploma, and professional courses) at recognized institutions. Annual family income must be below Rs 2.5 lakh (SC Post-Matric) or Rs 1 lakh (OBC Post-Matric). For ST: Scheduled Tribe students in Class 11 and above with family income below Rs 2.5 lakh."
    ],
    "benefits": [
      "Maintenance allowance (stipend) covering living expenses varying by course level and day scholar/hosteller status.",
      "Compulsory non-refundable fees: tuition, examination, library, sports, and other mandatory fees reimbursed.",
      "Hostellers: Rs 1,200–1,300 per month maintenance allowance; Day Scholars: Rs 550–750 per month (rates vary by course level).",
      "Additional allowances for students with disabilities.",
      "Coverage includes professional courses like MBBS, BDS, B.Tech, LLB, B.Ed, CA, ICWA, and others."
    ],
    "documents": [
      "Aadhaar Card",
      "Caste certificate (SC/ST/OBC) issued by competent authority",
      "Income certificate (annual family income below threshold)",
      "Mark sheet of qualifying examination",
      "Bonafide student certificate from institution",
      "Bank account details (student's own account)",
      "Photograph",
      "Institution enrollment/admission letter"
    ],
    "howToApply": [
      "Apply online through the National Scholarship Portal (scholarships.gov.in) at the start of the academic year. First-time applicants register on NSP and fill the scholarship application for the relevant scheme. Renewal applications must be submitted each year. Applications are verified by respective states/institutions."
    ],
    "whereToApply": "Apply online through the National Scholarship Portal (scholarships.gov.in) at the start of the academic year. First-time applicants register on NSP an",
    "conditions": [
      "Income limit varies by scheme: SC and ST — Rs 2.5 lakh per annum; OBC — Rs 1 lakh per annum.",
      "Scholarship is renewable annually subject to satisfactory progress in studies.",
      "Only one post-matric scholarship can be availed at a time; students must not be availing other central/state scholarships simultaneously.",
      "Application window is open from August to November each academic year on NSP — deadlines must be observed.",
      "Marks/grade requirements vary — students should check the specific scheme guidelines on NSP."
    ],
    "source": {
      "label": "National Scholarship Portal",
      "url": "https://scholarships.gov.in/"
    }
  },
  {
    "slug": "pre-matric-scholarship",
    "name": "Pre-Matric Scholarship for SC, ST, OBC, Minority Students",
    "category": "Students",
    "image": "/images/categories/education.svg",
    "summary": "Pre-Matric Scholarships are Central Sector Scholarships to support students from Scheduled Castes, Scheduled Tribes, OBC, and Minority communities in Classes 9 and 10 to continue their education and reduce dropout rates at the secondary school level.",
    "description": "Pre-Matric Scholarships are Central Sector Scholarships to support students from Scheduled Castes, Scheduled Tribes, OBC, and Minority communities in Classes 9 and 10 to continue their education and reduce dropout rates at the secondary school level. The scheme provides financial assistance for maintenance and fees during the critical pre-matric stage to prevent exclusion of underprivileged students.",
    "eligibility": [
      "Students from SC/ST/OBC/Minority communities studying in Classes 9 and 10 at recognized schools. Annual family income criteria: OBC Pre-Matric — below Rs 1 lakh; SC/ST Pre-Matric — below Rs 2.5 lakh; Minority Pre-Matric — below Rs 1 lakh. Minimum 50% marks in previous class (for renewal). Students whose parents are engaged in unclean occupations are given priority."
    ],
    "benefits": [
      "Maintenance allowance for hostellers: Rs 750–1,000 per month depending on category (Class 9 and 10).",
      "Maintenance allowance for day scholars: Rs 150–250 per month.",
      "Reimbursement of mandatory school fees: tuition, exam, library, sports fees.",
      "Disability allowance for students with PwD status.",
      "Separate scholarships available under Minority Pre-Matric (Ministry of Minority Affairs) for Muslim, Christian, Sikh, Buddhist, Jain, and Zoroastrian communities."
    ],
    "documents": [
      "Aadhaar Card of student",
      "Caste/category certificate issued by competent authority",
      "Income certificate of parent/guardian",
      "Mark sheet of previous class examination",
      "School enrollment/bonafide certificate",
      "Bank account details in the student's or parent's name",
      "Photograph"
    ],
    "howToApply": [
      "Apply online at the National Scholarship Portal (scholarships.gov.in) before the deadline (typically August–October each year). Students register on NSP, select the appropriate pre-matric scholarship scheme, and fill in personal, family income, and academic details. Applications are verified by school and district authorities before disbursement."
    ],
    "whereToApply": "Apply online at the National Scholarship Portal (scholarships.gov.in) before the deadline (typically August–October each year). Students register on N",
    "conditions": [
      "Available only for Classes 9 and 10 — students in Classes 1–8 are covered under state scholarship or Samagra Shiksha.",
      "Only one scholarship at a time — students must not simultaneously receive other central scholarships.",
      "Annual income limits differ by community — verify the exact threshold for your category on NSP.",
      "Application deadlines are strictly enforced on NSP; late applications are not entertained."
    ],
    "source": {
      "label": "National Scholarship Portal",
      "url": "https://scholarships.gov.in/"
    }
  },
  {
    "slug": "samagra-shiksha",
    "name": "Samagra Shiksha Abhiyan",
    "category": "Students",
    "image": "/images/categories/education.svg",
    "summary": "Samagra Shiksha is a comprehensive programme for school education extending from pre-school (Balvatikas) to Class 12, launched in 2018 as an integrated scheme merging Sarva Shiksha Abhiyan (SSA), Rashtriya Madhyamik Shiksha Abhiyan (RMSA), and Teachers Education (TE).",
    "description": "Samagra Shiksha is a comprehensive programme for school education extending from pre-school (Balvatikas) to Class 12, launched in 2018 as an integrated scheme merging Sarva Shiksha Abhiyan (SSA), Rashtriya Madhyamik Shiksha Abhiyan (RMSA), and Teachers Education (TE). It aims to ensure inclusive and equitable quality education and promote lifelong learning opportunities, with a holistic approach to school effectiveness from early childhood to senior secondary level.",
    "eligibility": [
      "All children aged 3–18 years in government and government-aided schools from pre-primary (Balvatika) to Class 12. Special focus on: girls, SC/ST, Persons with Disabilities (PwD), children in difficult circumstances, Educationally Backward Blocks, Left Wing Extremism-affected areas, and aspirational districts."
    ],
    "benefits": [
      "Free and compulsory school education from Classes 1–8 under RTE Act, implemented through Samagra Shiksha.",
      "Free uniforms for girls and boys (2 sets per year) in Classes 1–8 in government schools.",
      "Free textbooks for students in Classes 1–8 under centrally sponsored norm.",
      "Stipend/scholarship for girls studying in Classes 9–12 in Kasturba Gandhi Balika Vidyalayas (KGBVs) and residential schools.",
      "Support for setting up KGBV residential schools for girls from disadvantaged communities at secondary level.",
      "ICT and digital initiatives: Smart Classrooms, virtual labs, DIKSHA platform for digital learning.",
      "Inclusive education support for children with special needs (CwSN) including assistive devices, escort allowance, and resource centres.",
      "Vocational education integration in Classes 9–12.",
      "Sports and physical education facilities in schools."
    ],
    "documents": [
      "Birth certificate for school enrollment",
      "Aadhaar Card",
      "Caste certificate (for priority scholarships and residential schools)",
      "Disability certificate (for CwSN support)",
      "Proof of residence"
    ],
    "howToApply": [
      "No individual application required. Benefits flow automatically to all students enrolled in government and government-aided schools. Parents should enroll their children in government schools to access scheme benefits. For KGBV residential school admission, contact the district education office. For children with special needs (CwSN), contact the Block Resource Centre."
    ],
    "whereToApply": "No individual application required. Benefits flow automatically to all students enrolled in government and government-aided schools. Parents should en",
    "conditions": [
      "The scheme covers government and government-aided schools only; private unaided schools are not directly covered.",
      "RTE provisions (free and compulsory education) apply to all children aged 6–14 years in neighborhood schools.",
      "Scheme norms and specific entitlements may vary by state as it is a Centrally Sponsored Scheme implemented through State Implementation Societies (SIS).",
      "KGBV residential schools are available for girls in Classes 6–12 from SC/ST/OBC/Minority communities and BPL families."
    ],
    "source": {
      "label": "Samagra Shiksha Portal",
      "url": "https://samagrashiksha.education.gov.in/"
    }
  },
  {
    "slug": "saubhagya",
    "name": "Pradhan Mantri Sahaj Bijli Har Ghar Yojana (Saubhagya)",
    "category": "Social Security",
    "image": "/images/categories/social.svg",
    "summary": "The Saubhagya scheme was launched by the Ministry of Power to achieve universal household electrification across India by providing electricity connections to all willing un-electrified rural households and poor households in urban areas.",
    "description": "The Saubhagya scheme was launched by the Ministry of Power to achieve universal household electrification across India by providing electricity connections to all willing un-electrified rural households and poor households in urban areas. Rural Electrification Corporation (REC) is the nodal agency.",
    "eligibility": [
      "All un-electrified rural households identified via SECC 2011 data. Economically poor households in urban areas. Non-poor rural households are also eligible for connection on payment of a nominal fee of Rs 500 (recoverable in 10 installments through monthly electricity bills)."
    ],
    "benefits": [
      "Free last-mile electricity service connection including service cable, smart/electronic electricity meter, single light point with LED bulb, and mobile charging point for all identified poor households.",
      "For un-electrified households located in remote and inaccessible areas where grid extension is not feasible, Solar Photovoltaic (SPV) based standalone systems (including battery bank, 5 LED lights, 1 DC fan, and 1 DC power plug) are provided with 5-year repair and maintenance support.",
      "Elimination of indoor kerosene pollution and improvement in health, education, and quality of life."
    ],
    "documents": [
      "Aadhaar Card or Voter ID Card",
      "Proof of residence / address proof",
      "Passport size photograph"
    ],
    "howToApply": [
      "Discoms (power distribution utilities) conduct door-to-door camps in villages and wards. Beneficiaries register on the spot using mobile apps deployed by local discom officials by submitting identification proof and address."
    ],
    "whereToApply": "Discoms (power distribution utilities) conduct door-to-door camps in villages and wards. Beneficiaries register on the spot using mobile apps deployed",
    "conditions": [
      "The connection infrastructure and installation are subsidized/free, but ongoing monthly electricity consumption charges must be paid by the consumer according to state DISCOM tariff schedules.",
      "Solar standalone systems are restricted to habitations where grid connection is techno-economically unfeasible.",
      "Households with illegal connections can regularize their connections under the scheme."
    ],
    "source": {
      "label": "Saubhagya Portal / Ministry of Power",
      "url": "https://powermin.gov.in/"
    }
  },
  {
    "slug": "soil-health-card",
    "name": "Soil Health Card (SHC) Scheme",
    "category": "Farmers",
    "image": "/images/categories/agriculture.svg",
    "summary": "The Soil Health Card Scheme was launched in 2015 to provide every farmer with a Soil Health Card containing crop-wise soil nutrient status and fertilizer recommendations to help farmers improve soil health and crop productivity through balanced use of nutrients.",
    "description": "The Soil Health Card Scheme was launched in 2015 to provide every farmer with a Soil Health Card containing crop-wise soil nutrient status and fertilizer recommendations to help farmers improve soil health and crop productivity through balanced use of nutrients. The card lists 12 soil parameters including macro- and micro-nutrients and recommends appropriate fertilizer and soil amendment dosages.",
    "eligibility": [
      "All farmers across India owning or cultivating agricultural land are eligible to get their soil tested and receive a Soil Health Card, free of cost. Priority is given to resource-poor farmers, small and marginal farmers, and farmers in nutrient-deficient areas."
    ],
    "benefits": [
      "Free soil testing for 12 parameters: pH, Electrical Conductivity, Organic Carbon, Nitrogen, Phosphorus, Potassium, Sulphur, Zinc, Boron, Iron, Manganese, and Copper.",
      "Crop-wise nutrient recommendations and fertilizer dosage advice to improve yield.",
      "Identification of soil deficiencies helps reduce unnecessary fertilizer expenditure.",
      "Card issued every 2 years to track changes in soil health.",
      "Online access to soil health reports through soilhealth.dac.gov.in."
    ],
    "documents": [
      "Aadhaar Card or any identity proof",
      "Details of agricultural land (survey number / Khasra number)",
      "Mobile number for SMS notifications"
    ],
    "howToApply": [
      "Farmers can request soil testing at the nearest Soil Testing Laboratory operated by the State Agriculture Department, or through the Village-Level Soil Testing Facility (STF) or Soil Health Card Camp held by the government. Samples are collected by agriculture department staff or farmers can submit soil samples at the designated collection centre. Results and recommendations are sent to the farmer as a physical card and are available online."
    ],
    "whereToApply": "Farmers can request soil testing at the nearest Soil Testing Laboratory operated by the State Agriculture Department, or through the Village-Level Soi",
    "conditions": [
      "One Soil Health Card is issued per plot of land, valid for 2 years.",
      "Soil sample collection follows the standard grid-based sampling method — ideally one sample per 2.5 hectares.",
      "The fertilizer recommendation on the card is advisory; farmers are encouraged to follow it for optimal crop productivity.",
      "The card is available in local languages for ease of use."
    ],
    "source": {
      "label": "Soil Health Card Portal",
      "url": "https://soilhealth.dac.gov.in/"
    }
  },
  {
    "slug": "stand-up-india",
    "name": "Stand-Up India Scheme",
    "category": "Small Businesses",
    "image": "/images/categories/business.svg",
    "summary": "Stand-Up India Scheme facilitates bank loans to Scheduled Caste (SC), Scheduled Tribe (ST), and Women borrowers for setting up greenfield enterprises in manufacturing, services, trading, or agriculture-allied activities.",
    "description": "Stand-Up India Scheme facilitates bank loans to Scheduled Caste (SC), Scheduled Tribe (ST), and Women borrowers for setting up greenfield enterprises in manufacturing, services, trading, or agriculture-allied activities.",
    "eligibility": [
      "SC/ST and/or woman entrepreneurs above 18 years of age setting up a greenfield project. In non-individual enterprises, at least 51% of shareholding and controlling stake must be held by an SC/ST or woman entrepreneur."
    ],
    "benefits": [
      "Bank loans between ₹10 lakh and ₹1 crore for setting up greenfield businesses.",
      "Composite loan covering term loan and working capital requirement.",
      "Credit Guarantee coverage under the Credit Guarantee Scheme for Stand-Up India (CGSSI).",
      "Handholding support via Stand-Up India portal, SIDBI, and NABARD."
    ],
    "documents": [
      "Identity proof (Aadhaar Card, Voter ID, PAN Card, Passport)",
      "Proof of SC/ST category (Caste Certificate, if applicable)",
      "Address proof of applicant and business unit",
      "Project report / Business plan detailing capital layout and financial projections",
      "Partnership deed / Memorandum & Articles of Association (for non-individual units showing >= 51% SC/ST/Woman ownership)",
      "Bank account statements for last 6 months"
    ],
    "howToApply": [
      "Borrowers can apply online through the Stand-Up India portal (standupmitra.in / myscheme.gov.in) or directly at commercial bank branches across the country."
    ],
    "whereToApply": "Borrowers can apply online through the Stand-Up India portal (standupmitra.in / myscheme.gov.in) or directly at commercial bank branches across the co",
    "conditions": [
      "Loan is strictly for greenfield projects (first-time venture in manufacturing, services, trading, or agriculture-allied sector).",
      "Borrower must not be in default to any bank or financial institution.",
      "Margin money required is up to 15% (which can be converged with eligible central/state subsidy schemes)."
    ],
    "source": {
      "label": "myScheme / Stand-Up India Portal",
      "url": "https://www.myscheme.gov.in/schemes/sui"
    }
  },
  {
    "slug": "startup-india",
    "name": "Startup India Initiative",
    "category": "Small Businesses",
    "image": "/images/categories/business.svg",
    "summary": "Startup India is a flagship initiative of the Government of India, launched in 2016 and spearheaded by the Department for Promotion of Industry and Internal Trade (DPIIT), Ministry of Commerce and Industry.",
    "description": "Startup India is a flagship initiative of the Government of India, launched in 2016 and spearheaded by the Department for Promotion of Industry and Internal Trade (DPIIT), Ministry of Commerce and Industry. It aims to build a robust ecosystem for nurturing innovation and startups in the country, driving sustainable economic growth and generating large-scale employment opportunities.",
    "eligibility": [
      "Entities incorporated as Private Limited Companies, Registered Partnership Firms, or Limited Liability Partnerships (LLP) in India within the past 10 years. Annual turnover must not have exceeded Rs 100 crore in any preceding financial year. The entity must be working towards innovation, development, or improvement of products or processes, or have a scalable business model with high potential of employment generation or wealth creation."
    ],
    "benefits": [
      "Income tax exemption under Section 80-IAC of the Income Tax Act for 3 consecutive financial years out of the first 10 years of incorporation (subject to Inter-Ministerial Board approval).",
      "Exemption from Angel Tax under Section 56(2)(viib) upon DPIIT recognition.",
      "Fast-tracked patent examination and up to 80% rebate on patent filing fees and 50% rebate on trademark filing fees.",
      "Self-certification compliance under 6 labor laws and 3 environmental laws for a period of up to 5 years.",
      "Access to the Fund of Funds for Startups (FFS) managed by SIDBI and the Startup India Seed Fund Scheme (SISFS) providing up to Rs 20 lakh for proof of concept and up to Rs 50 lakh for commercialization."
    ],
    "documents": [
      "Certificate of Incorporation / Registration of Partnership",
      "PAN Card of the company/entity",
      "Brief write-up and presentation describing innovation, uniqueness, and scalability",
      "Website link, video, or prototype demonstration link"
    ],
    "howToApply": [
      "Founders register their incorporated company on the Startup India portal (startupindia.gov.in) and apply for DPIIT Recognition by providing company incorporation documents, brief description of the innovative product/service, and pitch deck."
    ],
    "whereToApply": "Founders register their incorporated company on the Startup India portal (startupindia.gov.in) and apply for DPIIT Recognition by providing company in",
    "conditions": [
      "An entity formed by splitting up or reconstruction of an existing business already in existence is NOT eligible.",
      "DPIIT recognition is required before applying for Section 80-IAC tax holiday or seed funding schemes.",
      "Turnover must remain below Rs 100 crore to maintain startup status during the 10-year period."
    ],
    "source": {
      "label": "Startup India Hub",
      "url": "https://www.startupindia.gov.in/"
    }
  },
  {
    "slug": "sukanya-samriddhi",
    "name": "Sukanya Samriddhi Account Scheme (SSAS)",
    "category": "Women",
    "image": "/images/categories/women.svg",
    "summary": "Sukanya Samriddhi Account Scheme is a government-backed small savings scheme targeted at parents or legal guardians of a girl child to build a dedicated financial reserve for her higher education and marriage expenses.",
    "description": "Sukanya Samriddhi Account Scheme is a government-backed small savings scheme targeted at parents or legal guardians of a girl child to build a dedicated financial reserve for her higher education and marriage expenses.",
    "eligibility": [
      "Account can be opened by a natural or legal guardian in the name of a girl child from her birth till she attains the age of 10 years. Only one account per girl child and maximum two accounts per family (except in cases of twins/triplets)."
    ],
    "benefits": [
      "Attractive government-notified interest rate (compounded annually).",
      "Tax exemption under Section 80C of the Income Tax Act for contributions made.",
      "Tax-free interest earned and maturity proceeds (EEE status).",
      "Partial withdrawal up to 50% of the balance permitted for higher education after the girl child reaches 18 years of age or passes 10th standard."
    ],
    "documents": [
      "Birth Certificate of the girl child",
      "Identity proof of the guardian (Aadhaar, PAN Card, Voter ID, Passport)",
      "Address proof of the guardian (Utility bill, Aadhaar, Passport)",
      "Photograph of the girl child and legal guardian",
      "Medical certificate in case of twin/triplet births (if claiming additional account)"
    ],
    "howToApply": [
      "Guardians can open a Sukanya Samriddhi Account by visiting any designated India Post Post Office branch or authorized public/private commercial bank branch with the prescribed account opening form."
    ],
    "whereToApply": "Guardians can open a Sukanya Samriddhi Account by visiting any designated India Post Post Office branch or authorized public/private commercial bank b",
    "conditions": [
      "Minimum annual deposit is ₹250 and maximum annual deposit is ₹1,50,000 in a financial year.",
      "Deposits can be made for 15 years from the date of opening.",
      "The account matures after 21 years from the date of account opening or at the time of marriage of the girl child after attaining 18 years.",
      "Failure to deposit the minimum amount in any financial year attracts a penalty fee of ₹50 along with the minimum required deposit."
    ],
    "source": {
      "label": "India Post / Ministry of Finance",
      "url": "https://www.indiapost.gov.in/"
    }
  },
  {
    "slug": "swachh-bharat-mission",
    "name": "Swachh Bharat Mission – Grameen (SBM-G / Phase II)",
    "category": "Healthcare",
    "image": "/images/categories/healthcare.svg",
    "summary": "Swachh Bharat Mission – Grameen Phase II focuses on sustaining the Open Defecation Free (ODF) status of rural India and managing solid and liquid waste (ODF Plus status) to maintain cleanliness in rural areas.",
    "description": "Swachh Bharat Mission – Grameen Phase II focuses on sustaining the Open Defecation Free (ODF) status of rural India and managing solid and liquid waste (ODF Plus status) to maintain cleanliness in rural areas.",
    "eligibility": [
      "Rural households in need of an Individual Household Latrine (IHHL), particularly Below Poverty Line (BPL) families and identified Above Poverty Line (APL) families (SC/ST, small/marginal farmers, landless laborers, physically handicapped, female-headed households)."
    ],
    "benefits": [
      "Financial incentive of ₹12,000 for the construction of Individual Household Latrine (IHHL) to eligible rural households (including central and state shares).",
      "Community Sanitary Complexes (CSC) established at village level for public hygiene.",
      "Solid and Liquid Waste Management (SLWM) infrastructure created across Gram Panchayats."
    ],
    "documents": [
      "Aadhaar Card",
      "Bank Account passbook/details linked with Aadhaar",
      "BPL Card / Category proof document",
      "Photograph of applicant and constructed/proposed toilet site"
    ],
    "howToApply": [
      "Eligible rural residents can apply online through the SBM-G portal (swachhbharatmission.ddws.gov.in) or submit an application through their respective Gram Panchayat / Village Sanitation Committee."
    ],
    "whereToApply": "Eligible rural residents can apply online through the SBM-G portal (swachhbharatmission.ddws.gov.in) or submit an application through their respective",
    "conditions": [
      "Financial incentive is disbursed upon verification of constructed toilet facility (geotagging).",
      "Priority is given to uncovered BPL households and vulnerable APL categories.",
      "Overall mission execution is coordinated through Gram Panchayats and District Water and Sanitation Missions (DWSM)."
    ],
    "source": {
      "label": "Swachh Bharat Mission – Grameen Portal",
      "url": "https://swachhbharatmission.ddws.gov.in/"
    }
  },
  {
    "slug": "women-helpline",
    "name": "Women Helpline Scheme (181)",
    "category": "Women",
    "image": "/images/categories/women.svg",
    "summary": "The Women Helpline (WHL) scheme provides a 24-hour toll-free telephonic emergency response service (short code 181) to women affected by violence or in distress.",
    "description": "The Women Helpline (WHL) scheme provides a 24-hour toll-free telephonic emergency response service (short code 181) to women affected by violence or in distress. Operational across all States and UTs, it provides immediate emergency referral services (police, hospital, ambulance) as well as non-emergency counseling, legal aid support, and information regarding government welfare schemes for women.",
    "eligibility": [
      "Any woman or adolescent girl facing physical violence, sexual abuse, mental or emotional harassment, domestic dispute, dowry harassment, cyberstalking, or distress. Available to any individual calling on behalf of an affected woman."
    ],
    "benefits": [
      "24x7 toll-free emergency call response via the 181 shortcode.",
      "Immediate linkage with Emergency Response Support System (ERSS 112), police PCR vans, ambulance services, and fire stations.",
      "Direct referral and coordination with One Stop Centres (Sakhi) for medical care, shelter, and legal counseling.",
      "Telephonic crisis counseling and psychological stabilization.",
      "Comprehensive guidance on state and central welfare schemes available for women."
    ],
    "documents": [
      "No documentation required. Emergency access is unconditional."
    ],
    "howToApply": [
      "Dial toll-free 181 from any mobile phone or landline in India at any time. The operator logs the call, triages the distress level, and mobilizes field response units or provides telephonic consultation immediately."
    ],
    "whereToApply": "Dial toll-free 181 from any mobile phone or landline in India at any time. The operator logs the call, triages the distress level, and mobilizes field",
    "conditions": [
      "The 181 service operates continuously 365 days a year across the country.",
      "Integrated directly with One Stop Centres (OSC) in every district.",
      "Call confidentiality and caller anonymity are protected by operational protocols."
    ],
    "source": {
      "label": "Ministry of Women and Child Development / Sambal Component of Mission Shakti",
      "url": "https://wcd.nic.in/"
    }
  }
];

export const getScheme = (slug: string) => schemes.find((s) => s.slug === slug);
