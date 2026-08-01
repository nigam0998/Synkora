"use client";

import React, { useEffect, useRef, useState } from "react";

interface AnimateOnScrollProps {
  children: React.ReactNode;
  animation?: "fadeIn" | "slideUp" | "slideLeft" | "scaleIn";
  delay?: number;
  threshold?: number;
  className?: string;
  once?: boolean;
}

const animationStyles: Record<string, React.CSSProperties> = {
  fadeIn: { opacity: 0, transform: "translateY(20px)" },
  slideUp: { opacity: 0, transform: "translateY(40px)" },
  slideLeft: { opacity: 0, transform: "translateX(-30px)" },
  scaleIn: { opacity: 0, transform: "scale(0.9)" },
};

const visibleStyle: React.CSSProperties = {
  opacity: 1,
  transform: "translateY(0) translateX(0) scale(1)",
};

export function AnimateOnScroll({
  children,
  animation = "fadeIn",
  delay = 0,
  threshold = 0.15,
  className,
  once = true,
}: AnimateOnScrollProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          if (once) observer.unobserve(element);
        } else if (!once) {
          setIsVisible(false);
        }
      },
      { threshold },
    );

    observer.observe(element);
    return () => observer.disconnect();
  }, [threshold, once]);

  return (
    <div
      ref={ref}
      className={className}
      style={{
        ...(isVisible ? visibleStyle : animationStyles[animation]),
        transition: `opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1) ${delay}ms, transform 0.7s cubic-bezier(0.16, 1, 0.3, 1) ${delay}ms`,
        willChange: "opacity, transform",
      }}
    >
      {children}
    </div>
  );
}
