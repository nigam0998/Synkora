import Link from "next/link";
import styles from "./page.module.css";

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
    description: "Link your GitHub account and select repositories to analyze.",
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
              <Link href="#how-it-works">How It Works</Link>
            </li>
            <li>
              <a href="https://github.com" target="_blank" rel="noopener">
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
            <Link href="/register" className={styles.btnPrimary} id="cta-hero-start">
              Start Free Analysis
              <span>→</span>
            </Link>
            <Link href="#features" className={styles.btnSecondary} id="cta-hero-learn">
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

      {/* ── Features ────────────────────────────────────────────── */}
      <section className={styles.features} id="features">
        <div className={styles.sectionHeader}>
          <span className={styles.sectionTag}>Features</span>
          <h2 className={styles.sectionTitle}>
            Everything You Need to
            <br />
            <span className="gradient-text">Understand Your Code</span>
          </h2>
          <p className={styles.sectionSubtitle}>
            From architecture visualization to AI-powered code reviews, Synkora
            gives your team superpowers.
          </p>
        </div>

        <div className={styles.featuresGrid}>
          {features.map((feature, index) => (
            <div
              key={index}
              className={styles.featureCard}
              id={`feature-${index}`}
            >
              <div className={styles.featureIcon}>{feature.icon}</div>
              <h3 className={styles.featureTitle}>{feature.title}</h3>
              <p className={styles.featureDescription}>
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ── How It Works ────────────────────────────────────────── */}
      <section className={styles.howItWorks} id="how-it-works">
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

        <div className={styles.stepsContainer}>
          {steps.map((step, index) => (
            <div key={index} className={styles.step}>
              <div className={styles.stepNumber}>{step.number}</div>
              <h3 className={styles.stepTitle}>{step.title}</h3>
              <p className={styles.stepDescription}>{step.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA ─────────────────────────────────────────────────── */}
      <section className={styles.cta} id="cta">
        <div className={styles.ctaBox}>
          <h2 className={styles.ctaTitle}>
            Ready to <span className="gradient-text">Evolve</span>?
          </h2>
          <p className={styles.ctaSubtitle}>
            Join thousands of developers who trust Synkora to understand,
            analyze, and improve their codebases.
          </p>
          <Link href="/register" className={styles.btnPrimary} id="cta-bottom-start">
            Start Free Analysis →
          </Link>
        </div>
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
              <Link href="#how-it-works">How It Works</Link>
            </li>
            <li>
              <a href="https://github.com" target="_blank" rel="noopener">
                GitHub
              </a>
            </li>
            <li>
              <Link href="/privacy">Privacy</Link>
            </li>
            <li>
              <Link href="/terms">Terms</Link>
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
