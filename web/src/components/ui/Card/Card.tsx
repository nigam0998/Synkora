import React from "react";
import styles from "./Card.module.css";

type CardVariant = "default" | "glass" | "elevated" | "outline";
type CardPadding = "none" | "sm" | "md" | "lg";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
  padding?: CardPadding;
  interactive?: boolean;
  glowTop?: boolean;
}

export function Card({
  variant = "default",
  padding = "md",
  interactive = false,
  glowTop = false,
  children,
  className,
  ...props
}: CardProps) {
  const classNames = [
    styles.card,
    styles[variant],
    padding === "none" ? styles.noPadding : styles[padding],
    interactive ? styles.interactive : "",
    glowTop ? styles.glowTop : "",
    className || "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={classNames} {...props}>
      {children}
    </div>
  );
}

/* ── Card Sub-components ──────────────────────────────── */

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export function CardHeader({ title, subtitle, action }: CardHeaderProps) {
  return (
    <div className={styles.header}>
      <div>
        <h3 className={styles.headerTitle}>{title}</h3>
        {subtitle && <p className={styles.headerSubtitle}>{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

export function CardBody({
  children,
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`${styles.body} ${className || ""}`} {...props}>
      {children}
    </div>
  );
}

export function CardFooter({
  children,
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`${styles.footer} ${className || ""}`} {...props}>
      {children}
    </div>
  );
}

export function CardDivider() {
  return <div className={styles.divider} />;
}
