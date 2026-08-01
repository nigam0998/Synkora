import Link from "next/link";
import styles from "./page.module.css";
import { AnimateOnScroll } from "@/components/AnimateOnScroll";

const features = [
  {
    icon: "🏗️",
    title: "Architecture Reconstruction",
    description:
      "Auto-generate interactive architecture diagrams from your codebase. Understand layers, services, and component relationships at a glance.",
  },
  {
    icon: "📊",
    title: "Code Evolution Timeline",
    description:
      "Visualize how your codebase evolved over time with commit history, author contributions, and file change frequency heatmaps.",
  },
  {
    icon: "🔍",
    title: "Semantic Code Search",
    description:
      "Search your entire codebase using natural language. Find functions, patterns, and logic without knowing exact file locations.",
  },
  {
    icon: "🤖",
    title: "AI Code Assistant",
    description:
      "Context-aware AI chat that deeply understands your repository. Ask questions, get explanations, and receive code reviews.",
  },
  {
    icon: "🕸️",
    title: "Dependency Graph",
    description:
      "Interactive force-directed visualization of all dependencies. Detect circular dependencies and outdated packages instantly.",
  },
  {
    icon: "🐛",
    title: "Bug Prediction",
    description:
      "Identify high-risk files before bugs appear using historical patterns, complexity analysis, and change frequency scoring.",
  },
  {
    icon: "📝",
    title: "Auto Documentation",
    description:
      "Generate comprehensive documentation from code analysis. Keep your docs in sync with your codebase effortlessly.",
  },
  {
    icon: "⚠️",
    title: "Technical Debt Detection",
    description:
      "Find code smells, duplications, complexity hotspots, and TODO backlogs. Prioritize what to refactor first.",
  },
  {
    icon: "🔒",
    title: "Security Scanning",
    description:
      "Detect common vulnerability patterns, hardcoded secrets, and insecure dependencies across your entire project.",
  },
];

const steps = [
  {
    number: "1",
    title: "Connect GitHub",
    description:
      "Link your GitHub account and select repositories to analyze.",
  },
  {
    number: "2",
    title: "Deep Analysis",
    description:
      "Synkora parses code, mines git history, and builds knowledge graphs.",
  },
  {
    number: "3",
    title: "Gain Insights",
    description:
      "Explore interactive dashboards, chat with AI, and evolve your software.",
  },
];

const pricingPlans = [
  {
    tier: "Starter",
    price: "$0",
    period: "/month",
    description: "Perfect for individual developers and open-source projects.",
    popular: false,
    features: [
      "3 repositories",
      "Basic code metrics",
      "Dependency graph",
      "Commit history timeline",
      "Community support",
    ],
    cta: "Start Free",
  },
  {
    tier: "Pro",
    price: "$29",
    period: "/month",
    description:
      "For professional developers and small teams who need deeper insights.",
    popular: true,
    features: [
      "Unlimited repositories",
      "AI Code Assistant",
      "Semantic code search",
      "Technical debt detection",
      "Bug prediction engine",
      "Architecture visualization",
      "Priority support",
    ],
    cta: "Start Pro Trial",
  },
  {
    tier: "Enterprise",
    price: "$99",
    period: "/month",
    description:
      "For engineering teams that need full-suite code intelligence.",
    popular: false,
    features: [
      "Everything in Pro",
      "Team collaboration",
      "Custom integrations",
      "Automated documentation",
      "Security scanning",
      "SSO & SAML",
      "Dedicated support & SLA",
      "On-premise deployment",
    ],
    cta: "Contact Sales",
  },
];

const testimonials = [
  {
    quote:
      "Synkora helped us identify architecture drift that would have taken weeks to discover manually. The dependency graph alone saved our migration project.",
    name: "Sarah Chen",
    role: "Staff Engineer, Vercel",
    initials: "SC",
  },
  {
    quote:
      "The AI assistant understands our codebase better than most new hires. It is like pair programming with someone who has read every line of code.",
    name: "Marcus Rivera",
    role: "CTO, DataFlow Labs",
    initials: "MR",
  },
  {
    quote:
      "We reduced our onboarding time by 60% after giving new engineers access to Synkora. The auto-generated documentation is incredibly accurate.",
    name: "Priya Patel",
    role: "Engineering Manager, Stripe",
    initials: "PP",
  },
];

const techStack = [
  { icon: "⚛️", name: "React" },
  { icon: "🐍", name: "Python" },
  { icon: "📘", name: "TypeScript" },
  { icon: "☕", name: "Java" },
  { icon: "🦀", name: "Rust" },
  { icon: "🐹", name: "Go" },
  { icon: "💎", name: "Ruby" },
  { icon: "🐘", name: "PHP" },
  { icon: "🔷", name: "C#" },
  { icon: "⚡", name: "Swift" },
  { icon: "🎯", name: "Kotlin" },
  { icon: "🐦", name: "Dart" },
];

export default function HomePage() {
  return (
    <>
      {/* ── Navbar ──────────────────────────────────────────────── */}
      <nav className={styles.navbar} id="navbar">
        <div className={styles.navContent}>
          <Link href="/" className={styles.navLogo}>
            <span className={styles.logoIcon}>🧬</span>
            Synkora
          </Link>
          <ul className={styles.navLinks}>
            <li>
              <Link href="#features">Features</Link>
            </li>
            <li>
              <Link href="#pricing">Pricing</Link>
            </li>
            <li>
              <Link href="#how-it-works">How It Works</Link>
            </li>
            <li>
              <a href="https://github.com/nigam0998/Synkora" target="_blank" rel="noopener">
                GitHub
              </a>
            </li>
          </ul>
          <div className={styles.navActions}>
            <Link
              href="/login"
              className={`${styles.btnNav} ${styles.btnNavGhost}`}
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className={`${styles.btnNav} ${styles.btnNavPrimary}`}
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ────────────────────────────────────────────────── */}
      <section className={styles.hero} id="hero">
        <div className={styles.heroContent}>
          <div className={styles.heroBadge}>
            <span className={styles.dot}></span>
            AI-Powered Code Intelligence
          </div>

          <h1 className={styles.heroTitle}>
            Understand Your
            <br />
            <span className={styles.highlight}>Software Evolution</span>
          </h1>

          <p className={styles.heroSubtitle}>
            Synkora analyzes your GitHub repositories to reconstruct
            architecture, detect technical debt, predict bugs, and provide
            AI-powered insights — all in one beautiful dashboard.
          </p>

          <div className={styles.heroActions}>
            <Link
              href="/register"
              className={styles.btnPrimary}
              id="cta-hero-start"
            >
              Start Free Analysis
              <span>→</span>
            </Link>
            <Link
              href="#features"
              className={styles.btnSecondary}
              id="cta-hero-learn"
            >
              See Features
            </Link>
          </div>

          <div className={styles.statsBar}>
            <div className={styles.statItem}>
              <div className={styles.statValue}>50+</div>
              <div className={styles.statLabel}>Languages Supported</div>
            </div>
            <div className={styles.statItem}>
              <div className={styles.statValue}>10K+</div>
              <div className={styles.statLabel}>Repos Analyzed</div>
            </div>
            <div className={styles.statItem}>
              <div className={styles.statValue}>99.9%</div>
              <div className={styles.statLabel}>Uptime SLA</div>
            </div>
            <div className={styles.statItem}>
              <div className={styles.statValue}>&lt;30s</div>
              <div className={styles.statLabel}>Avg Analysis Time</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Tech Stack Marquee ──────────────────────────────────── */}
      <div className={styles.techMarquee}>
        <div className={styles.marqueeTrack}>
          {/* Duplicate for infinite scroll */}
          {[...techStack, ...techStack].map((tech, index) => (
            <div key={index} className={styles.marqueeItem}>
              <span>{tech.icon}</span>
              {tech.name}
            </div>
          ))}
        </div>
      </div>

      {/* ── Features ────────────────────────────────────────────── */}
      <section className={styles.features} id="features">
        <AnimateOnScroll animation="fadeIn">
          <div className={styles.sectionHeader}>
            <span className={styles.sectionTag}>Features</span>
            <h2 className={styles.sectionTitle}>
              Everything You Need to
              <br />
              <span className="gradient-text">Understand Your Code</span>
            </h2>
            <p className={styles.sectionSubtitle}>
              From architecture visualization to AI-powered code reviews,
              Synkora gives your team superpowers.
            </p>
          </div>
        </AnimateOnScroll>

        <div className={styles.featuresGrid}>
          {features.map((feature, index) => (
            <AnimateOnScroll
              key={index}
              animation="slideUp"
              delay={index * 80}
            >
              <div className={styles.featureCard} id={`feature-${index}`}>
                <div className={styles.featureIcon}>{feature.icon}</div>
                <h3 className={styles.featureTitle}>{feature.title}</h3>
                <p className={styles.featureDescription}>
                  {feature.description}
                </p>
              </div>
            </AnimateOnScroll>
          ))}
        </div>
      </section>

      {/* ── How It Works ────────────────────────────────────────── */}
      <section className={styles.howItWorks} id="how-it-works">
        <AnimateOnScroll animation="fadeIn">
          <div className={styles.sectionHeader}>
            <span className={styles.sectionTag}>How It Works</span>
            <h2 className={styles.sectionTitle}>
              Three Steps to
              <br />
              <span className="gradient-text">Code Intelligence</span>
            </h2>
            <p className={styles.sectionSubtitle}>
              Get started in minutes, gain insights in seconds.
            </p>
          </div>
        </AnimateOnScroll>

        <div className={styles.stepsContainer}>
          {steps.map((step, index) => (
            <AnimateOnScroll
              key={index}
              animation="slideUp"
              delay={index * 150}
            >
              <div className={styles.step}>
                <div className={styles.stepNumber}>{step.number}</div>
                <h3 className={styles.stepTitle}>{step.title}</h3>
                <p className={styles.stepDescription}>{step.description}</p>
              </div>
            </AnimateOnScroll>
          ))}
        </div>
      </section>

      {/* ── Pricing ─────────────────────────────────────────────── */}
      <section className={styles.pricing} id="pricing">
        <AnimateOnScroll animation="fadeIn">
          <div className={styles.sectionHeader}>
            <span className={styles.sectionTag}>Pricing</span>
            <h2 className={styles.sectionTitle}>
              Simple, Transparent
              <br />
              <span className="gradient-text">Pricing</span>
            </h2>
            <p className={styles.sectionSubtitle}>
              Start free. Upgrade when you need more power.
            </p>
          </div>
        </AnimateOnScroll>

        <div className={styles.pricingGrid}>
          {pricingPlans.map((plan, index) => (
            <AnimateOnScroll
              key={index}
              animation="slideUp"
              delay={index * 120}
            >
              <div
                className={`${styles.pricingCard} ${plan.popular ? styles.pricingCardPopular : ""}`}
                id={`pricing-${plan.tier.toLowerCase()}`}
              >
                {plan.popular && (
                  <div className={styles.popularBadge}>Most Popular</div>
                )}
                <div className={styles.pricingTier}>{plan.tier}</div>
                <div className={styles.pricingPrice}>
                  <span className={styles.priceAmount}>{plan.price}</span>
                  <span className={styles.pricePeriod}>{plan.period}</span>
                </div>
                <p className={styles.pricingDescription}>
                  {plan.description}
                </p>
                <ul className={styles.pricingFeatures}>
                  {plan.features.map((feature, fIndex) => (
                    <li key={fIndex}>
                      <span className={styles.checkIcon}>✓</span>
                      {feature}
                    </li>
                  ))}
                </ul>
                <Link
                  href="/register"
                  className={`${styles.pricingCta} ${plan.popular ? styles.pricingCtaPrimary : styles.pricingCtaDefault}`}
                >
                  {plan.cta}
                </Link>
              </div>
            </AnimateOnScroll>
          ))}
        </div>
      </section>

      {/* ── Testimonials ────────────────────────────────────────── */}
      <section className={styles.testimonials} id="testimonials">
        <AnimateOnScroll animation="fadeIn">
          <div className={styles.sectionHeader}>
            <span className={styles.sectionTag}>Testimonials</span>
            <h2 className={styles.sectionTitle}>
              Loved by
              <br />
              <span className="gradient-text">Engineering Teams</span>
            </h2>
            <p className={styles.sectionSubtitle}>
              See what developers and engineering leaders are saying.
            </p>
          </div>
        </AnimateOnScroll>

        <div className={styles.testimonialsGrid}>
          {testimonials.map((testimonial, index) => (
            <AnimateOnScroll
              key={index}
              animation="slideUp"
              delay={index * 120}
            >
              <div className={styles.testimonialCard}>
                <div className={styles.testimonialStars}>
                  {"★★★★★".split("").map((star, i) => (
                    <span key={i}>{star}</span>
                  ))}
                </div>
                <p className={styles.testimonialQuote}>
                  &ldquo;{testimonial.quote}&rdquo;
                </p>
                <div className={styles.testimonialAuthor}>
                  <div className={styles.testimonialAvatar}>
                    {testimonial.initials}
                  </div>
                  <div>
                    <div className={styles.testimonialName}>
                      {testimonial.name}
                    </div>
                    <div className={styles.testimonialRole}>
                      {testimonial.role}
                    </div>
                  </div>
                </div>
              </div>
            </AnimateOnScroll>
          ))}
        </div>
      </section>

      {/* ── CTA ─────────────────────────────────────────────────── */}
      <section className={styles.cta} id="cta">
        <AnimateOnScroll animation="scaleIn">
          <div className={styles.ctaBox}>
            <h2 className={styles.ctaTitle}>
              Ready to <span className="gradient-text">Evolve</span>?
            </h2>
            <p className={styles.ctaSubtitle}>
              Join thousands of developers who trust Synkora to understand,
              analyze, and improve their codebases.
            </p>
            <Link
              href="/register"
              className={styles.btnPrimary}
              id="cta-bottom-start"
            >
              Start Free Analysis →
            </Link>
          </div>
        </AnimateOnScroll>
      </section>

      {/* ── Footer ──────────────────────────────────────────────── */}
      <footer className={styles.footer} id="footer">
        <div className={styles.footerContent}>
          <div className={styles.footerLogo}>
            <span className={styles.logoIcon}>🧬</span>
            Synkora
          </div>
          <ul className={styles.footerLinks}>
            <li>
              <Link href="#features">Features</Link>
            </li>
            <li>
              <Link href="#pricing">Pricing</Link>
            </li>
            <li>
              <Link href="#how-it-works">How It Works</Link>
            </li>
            <li>
              <a href="https://github.com/nigam0998/Synkora" target="_blank" rel="noopener">
                GitHub
              </a>
            </li>
            <li>
              <Link href="/privacy">Privacy</Link>
            </li>
          </ul>
          <span className={styles.footerCopy}>
            © 2026 Synkora. All rights reserved.
          </span>
        </div>
      </footer>
    </>
  );
}
