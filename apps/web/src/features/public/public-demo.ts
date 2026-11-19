export type InformationArticle = {
  slug: string;
  title: string;
  category: "Voter registration" | "PVC" | "Polling units" | "Voting procedures" | "Election dates";
  summary: string;
  updatedAt: string;
  sourceName: string;
  content: string[];
};

export type FactCheck = {
  slug: string;
  verdict: "confirmed" | "contradicted" | "no_official_statement";
  title: string;
  summary: string;
  topic: "Voter registration" | "PVC" | "Voting procedures";
  publishedAt: string;
  originalClaim: string;
  investigation: string[];
};

export const demonstrationNotice =
  "Demonstration content only. These examples are not published election guidance or real fact-check verdicts.";

export const informationArticles: InformationArticle[] = [
  {
    slug: "preparing-for-voter-registration",
    title: "Preparing for voter registration",
    category: "Voter registration",
    summary:
      "A clear checklist of documents and questions to confirm before beginning registration.",
    updatedAt: "18 Nov 2026",
    sourceName: "Example official publication",
    content: [
      "Confirm the current registration window through a verified official source.",
      "Prepare acceptable identification and keep copies of any required supporting information.",
      "Use an official registration location or approved online channel named by the election authority.",
      "Check your registration status before election day and report any discrepancy through an official channel.",
    ],
  },
  {
    slug: "checking-your-pvc",
    title: "Checking your permanent voter card",
    category: "PVC",
    summary:
      "Understand where to check collection information and how to protect your personal details.",
    updatedAt: "16 Nov 2026",
    sourceName: "Example official publication",
    content: [
      "Confirm collection instructions through the election authority's official website or office.",
      "Carry only the identification requested for collection.",
      "Do not share card numbers or other personal details in forwarded messages.",
      "Ask an official office for help if the card cannot be found or appears incorrect.",
    ],
  },
  {
    slug: "finding-a-polling-unit",
    title: "Finding your polling unit",
    category: "Polling units",
    summary: "A simple process for verifying a polling location before election day.",
    updatedAt: "14 Nov 2026",
    sourceName: "Example official publication",
    content: [
      "Check the official polling-unit lookup provided by the election authority.",
      "Confirm the result again close to election day because arrangements can change.",
      "Ask for written confirmation if information differs across sources.",
      "Never rely on a forwarded screenshot as the only location notice.",
    ],
  },
  {
    slug: "understanding-the-voting-process",
    title: "Understanding the voting process",
    category: "Voting procedures",
    summary: "Know the basic steps, what to expect at the polling unit and when to ask for help.",
    updatedAt: "12 Nov 2026",
    sourceName: "Example official publication",
    content: [
      "Follow the directions of accredited polling-unit officials.",
      "Confirm your identity and name using the official process.",
      "Ask questions quietly and do not obstruct other voters.",
      "Report concerns through the official complaint channels rather than forwarding an unverified claim.",
    ],
  },
  {
    slug: "checking-election-dates",
    title: "Checking election dates",
    category: "Election dates",
    summary: "How to verify election and registration dates before acting on a message.",
    updatedAt: "10 Nov 2026",
    sourceName: "Example official publication",
    content: [
      "Compare a date claim with the election authority's official timetable.",
      "Check the publication date of every message or screenshot.",
      "Treat amended dates as provisional until confirmed by an official notice.",
      "Share the official page or document, not only a cropped image.",
    ],
  },
];

export const factChecks: FactCheck[] = [
  {
    slug: "voter-registration-extension-example",
    verdict: "no_official_statement",
    title: "Example: a forwarded message claims voter registration has been extended",
    summary:
      "This demonstration checks how an unanswered claim should be presented when no official passage is available.",
    topic: "Voter registration",
    publishedAt: "19 Nov 2026",
    originalClaim: "Registration has been extended nationwide until next month.",
    investigation: [
      "The claim is specific enough to compare with an official registration timetable.",
      "No official source passage is included in this demonstration.",
      "The safest public answer is that no official statement has been found yet.",
    ],
  },
  {
    slug: "pvc-collection-example",
    verdict: "contradicted",
    title: "Example: PVC collection claim omits an important detail",
    summary:
      "This demonstration shows how supporting context should accompany a contradicted result.",
    topic: "PVC",
    publishedAt: "18 Nov 2026",
    originalClaim: "You can collect every PVC from one central location.",
    investigation: [
      "The claim appears to apply a general instruction to every voter.",
      "An official process would identify a designated polling or collection location.",
      "This route should link to the exact official passage used to reject or constrain the claim.",
    ],
  },
  {
    slug: "polling-unit-example",
    verdict: "confirmed",
    title: "Example: an official polling-unit address notice",
    summary: "This demonstration explains how an evidence-backed confirmed result is presented.",
    topic: "Voting procedures",
    publishedAt: "17 Nov 2026",
    originalClaim: "The polling-unit address was published on the official portal.",
    investigation: [
      "The example claim can be compared with an official address notice.",
      "The public page should quote the relevant passage and link to the full document.",
      "A confirmed result is only shown when the official source supports it.",
    ],
  },
];
