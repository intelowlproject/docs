import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/**
 * Markdown renderer for assistant chat messages.
 *
 * Kept separate from the shared `markdownToHtml` on purpose: the chat enables GFM (tables /
 * strikethrough / task lists) because the agent renders job and analyzer summaries as markdown
 * tables, which the shared renderer (no GFM) would show as broken pipe-text. Isolating it here
 * avoids changing how the rest of IntelOwl renders markdown.
 *
 * No `rehype-raw`: react-markdown v8 does not render raw HTML by default, so untrusted LLM output
 * stays XSS-safe without an extra sanitizer.
 * @param {string} text
 */
export function chatMarkdownToHtml(text) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      // eslint-disable-next-line react/no-children-prop
      children={text}
      components={{
        // eslint-disable-next-line id-length
        em: ({ node: _, ...props }) => <i className="text-code" {...props} />,
        // eslint-disable-next-line id-length
        a: ({ node: _, ...props }) => (
          // eslint-disable-next-line jsx-a11y/anchor-has-content
          <a
            target="_blank"
            rel="noopener noreferrer"
            className="link-primary"
            {...props}
          />
        ),
        table: ({ node: _, ...props }) => (
          <table className="table table-sm" {...props} />
        ),
        // drop react-markdown's `inline` flag so it is not spread onto the DOM node
        code: ({ node: _, inline: _inline, ...props }) => (
          <code className="text-code" {...props} />
        ),
      }}
    />
  );
}
