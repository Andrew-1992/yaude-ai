// Renders a fenced code block with a copy button in the top-right corner.
// Used as react-markdown's custom renderer for <pre><code> blocks --
// plain monospace text, no syntax-highlighting colors (see MessageBubble
// for why: it would break the black/cream/white discipline).

"use client";

import { useState } from "react";

interface CodeBlockProps {
  children: string;
}

export default function CodeBlock({ children }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(children);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard API unavailable (e.g. non-HTTPS context) -- fail silently.
    }
  }

  return (
    <div className="relative group/code">
      <button
        type="button"
        onClick={handleCopy}
        className="absolute top-2 right-2 text-[0.6875rem] px-2 py-1 rounded-md bg-sanadi-cream/10 text-sanadi-cream/70 hover:text-sanadi-cream hover:bg-sanadi-cream/20 opacity-0 group-hover/code:opacity-100 transition-opacity"
      >
        {copied ? "Copied" : "Copy"}
      </button>
      <pre>
        <code>{children}</code>
      </pre>
    </div>
  );
}
