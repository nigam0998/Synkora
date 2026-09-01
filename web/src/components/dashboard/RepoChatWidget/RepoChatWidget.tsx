"use client";

import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import { api } from "@/lib/api";
import styles from "./RepoChatWidget.module.css";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

interface CodeContext {
  file_path: string;
  content_type: string;
  content: string;
  line_start?: number;
  line_end?: number;
  relevance_score: number;
}

interface ChatResponseData {
  answer: string;
  code_context: CodeContext[];
  model: string;
  tokens_used: number;
}

export function RepoChatWidget({ repositoryId }: { repositoryId: string }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [contexts, setContexts] = useState<Record<number, CodeContext[]>>({});
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (isOpen && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen]);

  const toggleChat = () => setIsOpen((prev) => !prev);

  const sendMessage = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    
    // Add user message to state
    const newMessages: ChatMessage[] = [...messages, { role: "user", content: userMessage }];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      const response = await api.post<ChatResponseData>("/api/v1/chat", {
        repository_id: repositoryId,
        message: userMessage,
        history: messages, // send history for context
        include_code_context: true,
        max_context_chunks: 5,
      });

      if (response.success && response.data) {
        const assistantIdx = newMessages.length;
        setMessages([...newMessages, { role: "assistant", content: response.data.answer }]);
        if (response.data.code_context && response.data.code_context.length > 0) {
          setContexts(prev => ({ ...prev, [assistantIdx]: response.data!.code_context }));
        }
      } else {
        setMessages([...newMessages, { role: "assistant", content: "Sorry, I encountered an error. Please try again." }]);
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages([...newMessages, { role: "assistant", content: "Sorry, I encountered an error connecting to the server." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className={styles.widgetContainer}>
      {isOpen && (
        <div className={styles.chatWindow}>
          <div className={styles.chatHeader}>
            <h3>✨ Codebase Copilot</h3>
            <button className={styles.closeButton} onClick={toggleChat} aria-label="Close chat">
              &times;
            </button>
          </div>

          <div className={styles.messagesContainer}>
            {messages.length === 0 && (
              <div style={{ textAlign: "center", color: "var(--color-text-secondary)", marginTop: "2rem" }}>
                <p>Ask me anything about this repository!</p>
                <p style={{ fontSize: "var(--text-xs)", opacity: 0.8 }}>
                  e.g. &quot;How does the authentication flow work?&quot; or &quot;Where is the database connected?&quot;
                </p>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div key={idx} className={`${styles.messageWrapper} ${styles[msg.role]}`}>
                <div className={`${styles.messageBubble} ${msg.role === 'assistant' ? styles.markdownContent : ''}`}>
                  {msg.role === "user" ? (
                    msg.content
                  ) : (
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        code({ inline, className, children, ...props }: React.ComponentPropsWithoutRef<"code"> & { inline?: boolean }) {
                          const match = /language-(\w+)/.exec(className || "");
                          return !inline && match ? (
                            <SyntaxHighlighter
                              style={vscDarkPlus as unknown as { [key: string]: React.CSSProperties }}
                              language={match[1]}
                              PreTag="div"
                              {...props}
                            >
                              {String(children).replace(/\n$/, "")}
                            </SyntaxHighlighter>
                          ) : (
                            <code className={className} {...props}>
                              {children}
                            </code>
                          );
                        },
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  )}
                </div>
                
                {/* Render Code Context if available for this assistant message */}
                {msg.role === "assistant" && contexts[idx] && (
                  <details className={styles.contextContainer}>
                    <summary className={styles.contextHeader}>
                      View Retrieved Code Context ({contexts[idx].length} chunks)
                    </summary>
                    <div className={styles.contextBody}>
                      {contexts[idx].map((ctx, i) => (
                        <div key={i} className={styles.contextChunk}>
                          <strong>{ctx.file_path}</strong>
                          {ctx.line_start && ctx.line_end ? ` (Lines ${ctx.line_start}-${ctx.line_end})` : ""}
                          <br />
                          <span style={{ opacity: 0.7 }}>Relevance: {(ctx.relevance_score * 100).toFixed(1)}%</span>
                        </div>
                      ))}
                    </div>
                  </details>
                )}
              </div>
            ))}

            {isLoading && (
              <div className={`${styles.messageWrapper} ${styles.assistant}`}>
                <div className={`${styles.messageBubble} ${styles.loadingIndicator}`}>
                  <div className={styles.dot}></div>
                  <div className={styles.dot}></div>
                  <div className={styles.dot}></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className={styles.inputForm} onSubmit={sendMessage}>
            <textarea
              className={styles.inputField}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about the code..."
              disabled={isLoading}
              rows={1}
            />
            <button type="submit" className={styles.sendButton} disabled={!input.trim() || isLoading}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </form>
        </div>
      )}

      {!isOpen && (
        <button className={styles.toggleButton} onClick={toggleChat} aria-label="Open chat">
          ✨
        </button>
      )}
    </div>
  );
}
