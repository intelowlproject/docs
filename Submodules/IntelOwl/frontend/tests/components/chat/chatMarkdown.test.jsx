import React from "react";
import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";

import { chatMarkdownToHtml } from "../../../src/components/chat/chatMarkdown";

describe("chatMarkdownToHtml", () => {
  test("renders a GFM table (the reason remark-gfm is added)", () => {
    const markdown = "| Job | Status |\n| --- | --- |\n| 1 | success |";
    render(<div>{chatMarkdownToHtml(markdown)}</div>);
    const table = screen.getByRole("table");
    expect(table).toBeInTheDocument();
    expect(table.className).toContain("table");
    expect(screen.getByText("success")).toBeInTheDocument();
  });

  test("renders links opening in a new tab", () => {
    render(<div>{chatMarkdownToHtml("[docs](https://example.com)")}</div>);
    const link = screen.getByRole("link", { name: "docs" });
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("href", "https://example.com");
  });

  test("renders bold text without GFM-specific syntax", () => {
    render(<div>{chatMarkdownToHtml("This is **bold**")}</div>);
    expect(screen.getByText("bold").tagName).toBe("STRONG");
  });
});
