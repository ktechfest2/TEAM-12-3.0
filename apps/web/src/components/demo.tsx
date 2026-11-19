"use client";

import { TestimonialGlobe } from "./ui/map";
import type { GlobeTestimonial } from "./ui/map";

// Names, companies and quotes are fictional. City coordinates are real.
// Ordered east to west, so autoplay keeps turning the globe the way it spins.
export const TESTIMONIAL_GLOBE_REVIEWS: GlobeTestimonial[] = [
  {
    id: "london",
    quote: "We replaced three spreadsheets with one shared board. Everyone finally works from the same numbers.",
    name: "Tom Whitfield",
    role: "Head of Operations",
    company: "Halden Freight",
    city: "London",
    country: "GB",
    lat: 51.51,
    lng: -0.13,
    image: "https://cdn.21st.dev/assets/mirror/c7/c7c0ce8b744e9b0be993f4c77ca6a1fd143613009ac78d7259b1382f8f5d5ee7.jpg",
    rating: 5,
    tone: 1,
  },
  {
    id: "sao-paulo",
    quote: "Our support team switched over in a single afternoon. Customers noticed the faster replies before we announced anything.",
    name: "Renata Alves",
    role: "Customer Care Lead",
    company: "Serra Saúde",
    city: "São Paulo",
    country: "BR",
    lat: -23.55,
    lng: -46.63,
    image: "https://cdn.21st.dev/assets/mirror/16/16d32005c4f9f9dd69f5592556706adfe25e2390ef09620f58c75a579347fa12.jpg",
    rating: 5,
    tone: 2,
  },
  {
    id: "toronto",
    quote: "Setup took less time than our weekly stand-up. It quietly became the tool everyone opens first.",
    name: "Claire Donovan",
    role: "Engineering Manager",
    company: "Northpine",
    city: "Toronto",
    country: "CA",
    lat: 43.65,
    lng: -79.38,
    image: "https://cdn.21st.dev/assets/mirror/04/048421df3dd90eb34a8ea8d887d0919a5cdd68d423e61f241838e08ea86bd4b8.jpg",
    rating: 4,
    tone: 3,
  },
  {
    id: "san-francisco",
    quote: "The API was the easiest integration we shipped this year. Two engineers had it live within a week.",
    name: "Daniel Ferreira",
    role: "CTO",
    company: "Fogline Labs",
    city: "San Francisco",
    country: "US",
    lat: 37.78,
    lng: -122.42,
    image: "https://cdn.21st.dev/assets/mirror/ca/ca3e4b8395345600b418e5e1c3071c2a2f20023935080f4bf1b4ec6aa1c4bf77.jpg",
    rating: 5,
    tone: 4,
  },
  {
    id: "sydney",
    quote: "I run a small studio, so I need tools that stay out of the way. This one does, and our clients like the reports.",
    name: "Ethan Cruz",
    role: "Founder",
    company: "Saltwater Studio",
    city: "Sydney",
    country: "AU",
    lat: -33.87,
    lng: 151.21,
    image: "https://cdn.21st.dev/assets/mirror/8d/8dfac02ac82a4da74a97aa7204ddeab94472747b4a5ca901b315fd3b5d0b0442.jpg",
    rating: 5,
    tone: 5,
  },
  {
    id: "seoul",
    quote: "Designers and engineers now review the same thing in one place. Handoffs that took days happen in one thread.",
    name: "Jiho Shin",
    role: "Design Lead",
    company: "Maru Commerce",
    city: "Seoul",
    country: "KR",
    lat: 37.57,
    lng: 126.98,
    image: "https://cdn.21st.dev/assets/mirror/6e/6e13bf20f9b06ba3ae6de1bba3c439c3a99c9ed4ad8b4fabaf49805e0e06ef3e.jpg",
    rating: 4,
    tone: 1,
  },
  {
    id: "singapore",
    quote: "Onboarding a new client used to mean a week of calls. Now most of them are set up before our first meeting.",
    name: "Sophie Laurent",
    role: "Client Success Director",
    company: "Tidewell",
    city: "Singapore",
    country: "SG",
    lat: 1.28,
    lng: 103.83,
    image: "https://cdn.21st.dev/assets/mirror/59/59102df0a316e3ddf2e8e5bf224d9811becc1b0597d06f8f2b138784b32c523d.jpg",
    rating: 5,
    tone: 2,
  },
  {
    id: "mumbai",
    quote: "The reports are clear enough to share with leadership as they are. That alone saves my team hours every month.",
    name: "Ananya Iyer",
    role: "Head of Data",
    company: "Monsoon Analytics",
    city: "Mumbai",
    country: "IN",
    lat: 19.08,
    lng: 72.88,
    image: "https://cdn.21st.dev/assets/mirror/86/86d806620e25a037119ee9b6e966f759d993493ff9ecd0f7eff4528a9e28cb56.jpg",
    rating: 5,
    tone: 3,
  },
  {
    id: "nairobi",
    quote: "Our field teams log every visit from their phones now. The numbers reach head office the same day.",
    name: "Wanjiru Kamau",
    role: "Operations Director",
    company: "Kilele Pay",
    city: "Nairobi",
    country: "KE",
    lat: -1.29,
    lng: 36.82,
    image: "https://cdn.21st.dev/assets/mirror/f1/f1f63b103464aaf5c485f9e9092eaf0fdb69610c97adba44174bf785f9297ba8.jpg",
    rating: 5,
    tone: 4,
  },
  {
    id: "cape-town",
    quote: "We run stores in four cities and the dashboard keeps them in step. Support answers quickly, day or night.",
    name: "Ruan Botha",
    role: "COO",
    company: "Tablecloth Retail",
    city: "Cape Town",
    country: "ZA",
    lat: -33.93,
    lng: 18.42,
    image: "https://cdn.21st.dev/assets/mirror/63/6362e1daf50fa4afc2daba84126fac2688e782680bdfdd95462e25f7bc0d219d.jpg",
    rating: 4,
    tone: 5,
  },
];

export default function TestimonialGlobeDemo({ autoplay = true }: { autoplay?: boolean }) {
  return (
    <div data-globe-demo className="flex min-h-svh w-full items-center justify-center bg-background text-foreground">
      <TestimonialGlobe
        items={TESTIMONIAL_GLOBE_REVIEWS}
        eyebrow="Trusted on every continent"
        heading="What customers say, from where they say it."
        autoplay={autoplay}
        interval={3000}
        action={
          <button
            type="button"
            className="inline-flex h-9 items-center gap-1.5 rounded-full bg-primary px-4 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
          >
            Read all reviews
            <svg viewBox="0 0 16 16" aria-hidden="true" className="size-3.5" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 8h9.5M8.5 4l4 4-4 4" />
            </svg>
          </button>
        }
      />
    </div>
  );
}
