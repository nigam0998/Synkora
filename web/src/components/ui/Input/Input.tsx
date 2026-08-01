import React from "react";
import styles from "./Input.module.css";

type InputSize = "sm" | "md" | "lg";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  inputSize?: InputSize;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
  required?: boolean;
}

export function Input({
  label,
  error,
  helperText,
  inputSize = "md",
  leftIcon,
  rightIcon,
  fullWidth = true,
  required = false,
  className,
  id,
  ...props
}: InputProps) {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, "-");

  const inputClassNames = [
    styles.input,
    styles[inputSize],
    leftIcon ? styles.hasLeftIcon : "",
    rightIcon ? styles.hasRightIcon : "",
    error ? styles.error : "",
    className || "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div
      className={styles.inputWrapper}
      style={fullWidth ? { width: "100%" } : undefined}
    >
      {label && (
        <label htmlFor={inputId} className={styles.label}>
          {label}
          {required && <span className={styles.required}>*</span>}
        </label>
      )}
      <div className={styles.inputContainer}>
        {leftIcon && <span className={styles.leftIcon}>{leftIcon}</span>}
        <input id={inputId} className={inputClassNames} {...props} />
        {rightIcon && <span className={styles.rightIcon}>{rightIcon}</span>}
      </div>
      {error && <span className={styles.errorMessage}>⚠ {error}</span>}
      {helperText && !error && (
        <span className={styles.helperText}>{helperText}</span>
      )}
    </div>
  );
}

/* ── Textarea Variant ─────────────────────────────────── */
interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
  required?: boolean;
}

export function Textarea({
  label,
  error,
  helperText,
  required = false,
  className,
  id,
  ...props
}: TextareaProps) {
  const textareaId = id || label?.toLowerCase().replace(/\s+/g, "-");

  return (
    <div className={styles.inputWrapper} style={{ width: "100%" }}>
      {label && (
        <label htmlFor={textareaId} className={styles.label}>
          {label}
          {required && <span className={styles.required}>*</span>}
        </label>
      )}
      <textarea
        id={textareaId}
        className={`${styles.input} ${styles.textarea} ${error ? styles.error : ""} ${className || ""}`}
        {...props}
      />
      {error && <span className={styles.errorMessage}>⚠ {error}</span>}
      {helperText && !error && (
        <span className={styles.helperText}>{helperText}</span>
      )}
    </div>
  );
}
