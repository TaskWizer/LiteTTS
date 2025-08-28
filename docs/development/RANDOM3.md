Audit the system end to end and fix any issues as well as improve these features. A baseline was created but it still needs a lot of work.

**Project:** Create the initial MVP landing page for TaskWizer

**Objective:** Build a modern, professional, and conversion-focused website to introduce TaskWizer, generate interest, capture leads, and direct traffic to our open-source repositories.

**Core Brand Messaging:**
- **Primary Headline:** "The AI-Powered Productivity OS"
- **Tagline:** "Smarter Tasks, Less Work."
- **Elevator Pitch:** "TaskWizer is a suite of open-source, AI-native tools designed to work seamlessly together. We're building a composable productivity operating system for the modern developer and team, starting with powerful components like LiteTTS."
- **Key Value Propositions:** Open Source, Privacy-Focused (Offline-First PWA), Deeply Integrated, Developer-Centric

**Technical Implementation Requirements:**

**Framework & Dependencies:**
- **Base Stack:** Vite + React 18 + TypeScript
- **Styling:** Tailwind CSS with a professional color scheme (deep blues, teals, or purples for AI/productivity theme, with bold accent colors for CTAs)
- **PWA Configuration:** Must be installable as a Progressive Web App with offline functionality
- **Deployment Target:** Structured and configured for Cloudflare Pages deployment
- **Code Quality:** Create reusable, clean React components with TypeScript interfaces

**Page Structure & Component Specifications:**

**1. Hero Section Component:**
- Logo placeholder area for "TaskWizer" branding
- Primary headline: "The AI-Powered Productivity OS"
- Sub-headline: "A suite of open-source tools, built for a single goal: to make your workflow smarter, not harder."
- Primary CTA button: "View on GitHub" (link to GitHub organization: https://github.com/TaskWizer)
- Secondary CTA button: "Join the Waitlist" (trigger modal or form)
- Visual placeholder for animated dashboard screenshot or abstract tool visualization

**2. Components Showcase Section:**
- Section title: "The Foundational Suite"
- 3-card grid layout with responsive design (1 column on mobile, 2-3 columns on desktop)

**Card 1 - LiteTTS:**
- Icon: Megaphone or sound waves (use Heroicons or Lucide React)
- Title: "TaskWizer LiteTTS"
- Description: "A high-performance, offline-first text-to-speech engine. Optimized for edge deployment with emotional control and ultra-low latency."
- CTA: "Explore LiteTTS on GitHub →" (link to specific repository when available)

**Card 2 - FlowIDE (Placeholder):**
- Icon: Code symbol (use Heroicons or Lucide React)
- Title: "TaskWizer FlowIDE"
- Description: "A lightweight, web-based code editor with PWA support and AI integration, designed for seamless workflow automation."
- CTA: "Coming Soon" (disabled state styling)

**Card 3 - SprintAI (Placeholder):**
- Icon: Kanban board (use Heroicons or Lucide React)
- Title: "TaskWizer SprintAI"
- Description: "An AI-driven project manager that automates best practices and integrates directly with your development pipeline."
- CTA: "Coming Soon" (disabled state styling)

**3. Vision Section Component:**
- Title: "More Than the Sum of Its Parts"
- Body text: "Individually, these tools are powerful. But TaskWizer is building towards something greater: a deeply integrated, AI-native operating system for productivity where your editor, your assistant, and your project manager work as one."
- Visual: Simple SVG diagram showing three components connecting to a central hub (create with Tailwind CSS or inline SVG)

**4. Call to Action Section Component:**
- Title: "Build With Us"
- Body text: "TaskWizer is built in the open. Star our repositories, contribute to the code, or join our community to shape the future of productivity."
- Action buttons: "Join our Discord" and "Follow on Twitter" (use placeholder links for now)

**5. Footer Component:**
- TaskWizer logo (text-based for now)
- Navigation links: "GitHub", "Discord", "Twitter", "Blog (Coming Soon)"
- Legal links: Privacy Policy and Terms of Service (create placeholder pages)
- Copyright notice: "© 2024 TaskWizer. All rights reserved."

**Functional Requirements:**

**Waitlist Implementation:**
- Modal component with form fields: Name (required), Email (required), and optional "How did you hear about us?" dropdown
- Form validation using React Hook Form or similar
- Form submission to simple backend (implement with Cloudflare Worker or integrate with Airtable/Google Forms)
- Success/error state handling with proper user feedback
- Email validation and basic spam protection

**Technical Standards:**
- **Responsive Design:** Mobile-first approach with breakpoints at sm (640px), md (768px), lg (1024px), xl (1280px)
- **SEO Optimization:**
  - Meta title: "TaskWizer - The AI-Powered Productivity OS"
  - Meta description: "Open-source, AI-native productivity tools that work seamlessly together. Build smarter workflows with TaskWizer's composable productivity operating system."
  - Open Graph tags for social sharing
  - Semantic HTML structure with proper heading hierarchy
- **Performance:**
  - Lighthouse score target: 90+ for all metrics
  - Image optimization and lazy loading
  - Code splitting for optimal bundle size
- **Accessibility:**
  - WCAG 2.1 AA compliance
  - Proper ARIA labels and roles
  - Keyboard navigation support
  - Color contrast ratios meeting accessibility standards

**File Structure Requirements:**
```
src/
├── components/
│   ├── ui/           # Reusable UI components (Button, Modal, etc.)
│   ├── sections/     # Page sections (Hero, Showcase, Vision, CTA, Footer)
│   └── layout/       # Layout components
├── hooks/            # Custom React hooks
├── types/            # TypeScript type definitions
├── utils/            # Utility functions
├── styles/           # Global styles and Tailwind config
└── assets/           # Images, icons, etc.
```

**Deliverables:**
1. Complete React/TypeScript codebase with Vite configuration and hot reload
2. Tailwind CSS styling with custom design system and consistent spacing/typography
3. PWA configuration files (manifest.json, service worker) with offline caching strategy
4. Cloudflare Pages deployment configuration (wrangler.toml, build settings)
5. SEO meta tags, structured data (JSON-LD), and sitemap.xml
6. Fully responsive design implementation tested on multiple devices
7. Functional waitlist form with validation and submission handling
8. Component documentation with Storybook or detailed README
9. TypeScript interfaces for all props, API responses, and data structures
10. Performance optimization (lazy loading, code splitting, image optimization)

**Implementation Plan:**
1. Set up project structure with Vite, React, TypeScript, and Tailwind CSS
2. Create base layout and routing structure
3. Implement reusable UI components (Button, Modal, Card, etc.)
4. Build page sections in order: Hero → Showcase → Vision → CTA → Footer
5. Implement waitlist functionality with form validation
6. Add PWA configuration and service worker
7. Optimize for SEO and accessibility
8. Configure Cloudflare Pages deployment
9. Test responsive design across devices
10. Performance optimization and final testing

**Success Criteria:**
- Landing page loads in under 3 seconds on 3G connection
- Lighthouse scores above 90 for Performance, Accessibility, Best Practices, and SEO
- Fully responsive design that works on devices from 320px to 1920px width
- Functional waitlist form with proper validation and error handling
- PWA installable on mobile devices with offline functionality
- All links and CTAs properly configured (even if pointing to placeholder destinations)
