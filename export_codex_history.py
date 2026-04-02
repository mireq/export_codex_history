#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, select_autoescape
from markdown_it import MarkdownIt


HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>{{ document_title }}</title>
	<style>
		:root {
			--bg: #0f0f0f;
			--surface: #1a1a1a;
			--surface-2: #202020;
			--surface-3: #262626;
			--surface-4: #171717;
			--border: #2d2d2d;
			--border-strong: #383838;
			--text: #f3f3f3;
			--muted: #a6a6a6;
			--muted-2: #7f7f7f;
			--accent: #00d4aa;
			--accent-soft: rgba(0, 212, 170, 0.12);
			--danger: #ff6b9d;
			--danger-soft: rgba(255, 107, 157, 0.12);
			--success: #00d4aa;
			--success-soft: rgba(0, 212, 170, 0.12);
			--user: #d2b06b;
			--assistant: #cfcfcf;
			--tool: #8d8d8d;
			--shadow: 0 2px 8px rgba(0, 0, 0, 0.28);
			--radius: 10px;
			--font-sans: "IBM Plex Sans", "Noto Sans", "Liberation Sans", sans-serif;
			--font-mono: "Iosevka", "JetBrains Mono", "SFMono-Regular", monospace;
		}

		* { box-sizing: border-box; }
		body {
			margin: 0;
			color: var(--text);
			font-family: var(--font-sans);
			background: var(--bg);
		}

		a {
			color: inherit;
			text-decoration: none;
		}

		.app {
			display: grid;
			grid-template-columns: 252px minmax(0, 1fr);
			min-height: 100vh;
		}

		.sidebar {
			background: var(--surface);
			border-right: 1px solid var(--border);
			padding: 20px 16px;
		}

		.sidebar-section + .sidebar-section {
			margin-top: 24px;
		}

		.sidebar-title {
			margin: 0 0 12px;
			font-size: 13px;
			font-weight: 600;
			color: var(--muted);
		}

		.meta-list,
		.turn-nav {
			display: grid;
			gap: 6px;
		}

		.meta-row {
			padding: 8px 10px;
			background: var(--surface-2);
			border: 1px solid var(--border);
			border-radius: 8px;
		}

		.meta-key {
			display: block;
			font-size: 12px;
			margin: 0;
			color: var(--muted);
		}

		.meta-value {
			display: block;
			margin-top: 2px;
			word-break: break-word;
			line-height: 1.45;
		}

		.turn-link {
			display: block;
			padding: 8px 10px;
			border: 1px solid var(--border);
			border-radius: 8px;
			background: var(--surface-2);
			color: var(--muted);
		}

		.turn-link:hover {
			border-color: var(--border-strong);
			color: var(--text);
		}

		.turn-link strong,
		.turn-link span {
			display: block;
		}

		.turn-link span {
			margin-top: 2px;
			color: var(--muted-2);
			font-size: 13px;
		}

		.main {
			min-width: 0;
		}

		.topbar {
			display: flex;
			justify-content: space-between;
			align-items: center;
			gap: 16px;
			min-height: 56px;
			padding: 0 24px;
			border-bottom: 1px solid var(--border);
			background: var(--surface);
		}

		.topbar-title {
			font-size: 16px;
			font-weight: 600;
		}

		.topbar-meta {
			color: var(--muted);
			font-size: 13px;
			text-align: right;
		}

		.content {
			padding: 24px;
		}

		.summary {
			display: grid;
			grid-template-columns: repeat(4, minmax(0, 1fr));
			gap: 0;
			margin-bottom: 24px;
			border: 1px solid var(--border);
			border-radius: 8px;
			background: var(--surface);
			overflow: hidden;
			box-shadow: var(--shadow);
		}

		.summary-item {
			padding: 12px 14px;
			border-right: 1px solid var(--border);
		}

		.summary-item:last-child { border-right: 0; }

		.summary-label {
			font-size: 12px;
			color: var(--muted);
		}

		.summary-value {
			margin-top: 4px;
			font-size: 20px;
			font-weight: 600;
		}

		.timeline {
			display: grid;
			gap: 16px;
		}

		.turn {
			background: var(--surface);
			border: 1px solid var(--border);
			border-radius: 10px;
			box-shadow: var(--shadow);
		}

		.turn-header {
			display: flex;
			justify-content: space-between;
			gap: 12px;
			align-items: center;
			padding: 14px 16px;
			border-bottom: 1px solid var(--border);
		}

		.turn-title {
			font-size: 14px;
			font-weight: 600;
		}

		.turn-subtitle,
		.turn-count {
			color: var(--muted);
			font-size: 13px;
		}

		.items {
			display: grid;
			gap: 0;
		}

		.item {
			padding: 14px 16px;
			border-bottom: 1px solid var(--border);
			background: transparent;
			opacity: 1;
		}

		.item:last-child {
			border-bottom: 0;
		}

		.item-header {
			display: flex;
			justify-content: space-between;
			gap: 12px;
			align-items: center;
			margin-bottom: 10px;
			min-width: 0;
		}

		.item-label {
			font-size: 13px;
			font-weight: 600;
			min-width: 0;
			flex: 1 1 auto;
		}

		.item-label code {
			display: block;
			font-family: var(--font-mono);
			font-size: 12px;
			font-weight: 500;
			color: var(--text);
			white-space: pre-wrap;
			overflow-wrap: anywhere;
			word-break: break-word;
		}

		.item.user .item-label { color: var(--user); }
		.item.assistant .item-label { color: var(--assistant); }
		.item.tool .item-label,
		.item.system .item-label { color: var(--tool); }

		.item.user {
			background: rgba(210, 176, 107, 0.06);
		}

		.item.assistant {
			background: rgba(255, 255, 255, 0.015);
		}

		.item.assistant .rich-text,
		.item.system .rich-text {
			color: #c9c9c9;
		}

		.item.assistant .timestamp,
		.item.system .timestamp,
		.item.tool .timestamp {
			color: var(--muted-2);
		}

		.item.tool,
		.item.system {
			background: var(--surface-4);
		}

		.item.tool {
			opacity: 0.82;
		}

		.item.tool:hover,
		.item.tool:focus-within,
		.item.system:hover,
		.item.system:focus-within {
			opacity: 1;
		}

		.item.assistant:not(.finalized) {
			opacity: 0.88;
		}

		.item.assistant.finalized {
			background: rgba(255, 255, 255, 0.045);
			border-top: 1px solid var(--border-strong);
			border-bottom-color: var(--border-strong);
			opacity: 1;
		}

		.item.assistant.finalized .item-label {
			color: #f0f0f0;
		}

		.item.assistant.finalized .rich-text {
			color: var(--text);
			font-size: 15px;
		}

		.item.tool.success {
			border-left: 3px solid var(--success);
			background: linear-gradient(90deg, rgba(0, 212, 170, 0.06), transparent 72px), var(--surface-4);
		}

		.item.tool.error {
			border-left: 3px solid var(--danger);
			background: linear-gradient(90deg, rgba(255, 107, 157, 0.06), transparent 72px), var(--surface-4);
		}

		.item.tool.success .item-label code {
			color: #8df0db;
		}

		.item.tool.error .item-label code {
			color: #ffabc4;
		}

		.timestamp {
			color: var(--muted);
			font-size: 12px;
			white-space: nowrap;
			flex: 0 0 auto;
		}

		.rich-text {
			line-height: 1.65;
			color: var(--text);
			font-size: 14px;
		}

		.rich-text :first-child { margin-top: 0; }
		.rich-text :last-child { margin-bottom: 0; }
		.rich-text pre {
			overflow-x: auto;
			max-width: 100%;
			padding: 12px;
			border-radius: 8px;
			background: #121212;
			color: var(--text);
			font-family: var(--font-mono);
			font-size: 13px;
			line-height: 1.5;
			border: 1px solid var(--border);
		}
		.rich-text code {
			font-family: var(--font-mono);
			font-size: 0.92em;
		}
		.rich-text p code, .rich-text li code {
			padding: 0.12rem 0.3rem;
			border-radius: 4px;
			background: #181818;
			border: 1px solid var(--border);
		}
		.rich-text blockquote {
			margin-left: 0;
			padding-left: 12px;
			border-left: 2px solid var(--border-strong);
			color: var(--muted);
		}

		.meta-note {
			margin-top: 10px;
			padding: 8px 10px;
			border: 1px solid var(--border);
			border-radius: 8px;
			background: var(--surface-2);
			color: var(--muted);
			font-size: 12px;
			line-height: 1.45;
		}

		.meta-note pre {
			margin: 6px 0 0;
			white-space: pre-wrap;
			word-break: break-word;
			font: 12px/1.45 var(--font-mono);
			color: var(--muted);
		}

		.tool-shell {
			margin: -14px -16px;
		}

		.tool-shell > summary {
			display: flex;
			justify-content: space-between;
			gap: 12px;
			align-items: center;
			padding: 14px 16px 10px;
			cursor: pointer;
			list-style: none;
		}

		.tool-shell > summary::-webkit-details-marker {
			display: none;
		}

		.tool-shell > summary::before {
			content: "▸";
			color: var(--muted);
			font-size: 11px;
			flex: 0 0 auto;
			margin-right: 8px;
		}

		.tool-shell[open] > summary::before {
			content: "▾";
		}

		.tool-shell > summary .item-header {
			margin-bottom: 0;
			flex: 1 1 auto;
		}

		.tool-panel {
			margin-top: 8px;
			border-radius: 8px;
			border: 1px solid var(--border);
			background: var(--surface-2);
			overflow: hidden;
		}

		.tool-panel {
			margin: 0 16px 14px;
		}

		.tool-panel.success {
			border-color: rgba(0, 212, 170, 0.3);
			background: rgba(0, 212, 170, 0.06);
		}

		.tool-panel.error {
			border-color: rgba(255, 107, 157, 0.32);
			background: rgba(255, 107, 157, 0.06);
		}

		.tool-meta {
			padding: 10px 12px 0;
			color: var(--muted);
			font-size: 11px;
			line-height: 1.45;
		}

		.tool-output {
			padding: 10px 12px 12px;
		}

		.code-block {
			margin: 0;
			overflow-x: auto;
			max-width: 100%;
			padding: 12px;
			border-radius: 8px;
			background: #121212;
			color: var(--text);
			border: 1px solid var(--border);
			font: 500 12px/1.55 var(--font-mono);
			white-space: pre-wrap;
			word-break: break-word;
			overflow-wrap: anywhere;
		}

		.footnote {
			margin-top: 16px;
			color: var(--muted);
			font-size: 12px;
		}

		@media (max-width: 960px) {
			.app { grid-template-columns: 1fr; }
			.sidebar { border-right: 0; border-bottom: 1px solid var(--border); }
			.summary { grid-template-columns: repeat(2, minmax(0, 1fr)); }
			.summary-item:nth-child(2n) { border-right: 0; }
			.summary-item:nth-child(n + 3) { border-top: 1px solid var(--border); }
			.topbar { padding: 0 16px; }
			.content { padding: 16px; }
			.turn-header, .item-header { flex-direction: column; align-items: start; }
		}

		@media (max-width: 640px) {
			.summary { grid-template-columns: 1fr; }
			.summary-item { border-right: 0; border-top: 1px solid var(--border); }
			.summary-item:first-child { border-top: 0; }
		}
	</style>
</head>
<body>
	<main class="app">
		<aside class="sidebar">
			<section class="sidebar-section">
				<div class="sidebar-title">Session</div>
				<div class="meta-list">
					{% for row in sidebar_rows %}
					<div class="meta-row">
						<span class="meta-key">{{ row.key }}</span>
						<span class="meta-value">{{ row.value }}</span>
					</div>
					{% endfor %}
				</div>
			</section>

			<section class="sidebar-section">
				<div class="sidebar-title">Turns</div>
				<nav class="turn-nav">
					{% for turn in turns %}
					<a class="turn-link" href="#{{ turn.anchor }}">
						<strong>Turn {{ loop.index }}</strong>
						<span>{{ turn.toc_label }}</span>
					</a>
					{% endfor %}
				</nav>
			</section>
		</aside>

		<section class="main">
			<header class="topbar">
				<div class="topbar-title">{{ header_title }}</div>
				<div class="topbar-meta">{{ header_subtitle }}</div>
			</header>

			<div class="content">
				<section class="summary">
					<div class="summary-item">
						<div class="summary-label">Turns</div>
						<div class="summary-value">{{ turns|length }}</div>
					</div>
					<div class="summary-item">
						<div class="summary-label">Messages</div>
						<div class="summary-value">{{ stats.messages }}</div>
					</div>
					<div class="summary-item">
						<div class="summary-label">Tool Calls</div>
						<div class="summary-value">{{ stats.tool_calls }}</div>
					</div>
					<div class="summary-item">
						<div class="summary-label">Started</div>
						<div class="summary-value">{{ stats.started_at }}</div>
					</div>
				</section>

				<section class="timeline">
				{% for turn in turns %}
				<article class="turn" id="{{ turn.anchor }}">
					<div class="turn-header">
						<div>
							<div class="turn-title">Turn {{ loop.index }}</div>
							<div class="turn-subtitle">{{ turn.heading }}</div>
						</div>
						<div class="turn-count">{{ turn.item_count }} items</div>
					</div>

					<div class="items">
						{% for item in turn.items %}
						<section class="item {{ item.kind }} {{ item.tone }}{% if item.badge == 'Assistant Final' %} finalized{% endif %}">
							{% if item.kind == "tool" %}
							<details class="tool-shell">
								<summary>
									<div class="item-header">
										<span class="item-label"{% if item.title_text %} title="{{ item.title_text }}"{% endif %}>{% if item.kind == "tool" %}<code>{{ item.badge }}</code>{% else %}{{ item.badge }}{% endif %}</span>
										{% if item.timestamp %}
										<span class="timestamp">{{ item.timestamp }}</span>
										{% endif %}
									</div>
								</summary>

								{% if item.html %}
								<div class="rich-text">{{ item.html | safe }}</div>
								{% endif %}

								{% if item.details %}
								<div class="tool-panel {{ item.tone }}">
									{% if item.meta_html %}
									<div class="tool-meta">{{ item.meta_html | safe }}</div>
									{% endif %}
									<div class="tool-output">
										<pre class="code-block">{{ item.tool_output }}</pre>
									</div>
								</div>
								{% endif %}
							</details>
							{% else %}
							<div class="item-header">
								<span class="item-label"{% if item.title_text %} title="{{ item.title_text }}"{% endif %}>{% if item.kind == "tool" %}<code>{{ item.badge }}</code>{% else %}{{ item.badge }}{% endif %}</span>
								{% if item.timestamp %}
								<span class="timestamp">{{ item.timestamp }}</span>
								{% endif %}
							</div>

							{% if item.html %}
							<div class="rich-text">{{ item.html | safe }}</div>
							{% endif %}

							{% if item.meta_html %}
							<div class="meta-note">{{ item.meta_html | safe }}</div>
							{% endif %}

							{% if item.details %}
							<div class="tool-panel {{ item.tone }}">
								{% if item.meta_html %}
								<div class="tool-meta">{{ item.meta_html | safe }}</div>
								{% endif %}
								<div class="tool-output">
									<pre class="code-block">{{ item.tool_output }}</pre>
								</div>
							</div>
							{% endif %}
							{% endif %}
						</section>
						{% endfor %}
					</div>
				</article>
				{% endfor %}
				</section>

				<div class="footnote">Generated from {{ source_name }}</div>
			</div>
		</section>
	</main>
</body>
</html>
"""


@dataclass
class DetailBlock:
	title: str
	body: str
	preview: str = ""
	tone: str = "neutral"
	open: bool = False


@dataclass
class TimelineItem:
	kind: str
	badge: str
	timestamp: str
	html: str = ""
	meta_html: str = ""
	title_text: str = ""
	tone: str = "neutral"
	tool_output: str = ""
	details: list[DetailBlock] = field(default_factory=list)


@dataclass
class Turn:
	turn_id: str
	anchor: str
	heading: str
	toc_label: str
	item_count: int
	items: list[TimelineItem]


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Export a Codex JSONL history file into a polished standalone HTML transcript."
	)
	parser.add_argument("input", type=Path, nargs="?", help="Path to the Codex history JSONL file.")
	parser.add_argument(
		"-o",
		"--output",
		type=Path,
		help="Output HTML file path. Defaults to <input stem>.html in the same directory.",
	)
	parser.add_argument(
		"--title",
		help="Optional document title override.",
	)
	return parser.parse_args()


def detect_input_file(explicit_path: Path | None) -> Path:
	if explicit_path:
	  return explicit_path
	matches = sorted(Path.cwd().glob("*.jsonl"))
	if not matches:
		raise SystemExit("No .jsonl history file found in the current directory.")
	if len(matches) > 1:
		names = ", ".join(path.name for path in matches)
		raise SystemExit(f"Multiple .jsonl files found. Please choose one explicitly: {names}")
	return matches[0]


def parse_timestamp(value: str | None) -> datetime | None:
	if not value:
		return None
	normalized = value.replace("Z", "+00:00")
	try:
		return datetime.fromisoformat(normalized)
	except ValueError:
		return None


def format_timestamp(value: str | None) -> str:
	dt = parse_timestamp(value)
	if dt is None:
		return ""
	return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def compact_timestamp(value: str | None) -> str:
	dt = parse_timestamp(value)
	if dt is None:
		return ""
	return dt.astimezone().strftime("%H:%M:%S")


def pretty_json(value: str) -> str:
	try:
		return sanitize_text(json.dumps(json.loads(value), indent=2, ensure_ascii=False))
	except json.JSONDecodeError:
		return sanitize_text(value)


def sanitize_text(value: str) -> str:
	cleaned: list[str] = []
	for char in value:
		if char in "\n\r\t" or ord(char) >= 32:
			cleaned.append(char)
		else:
			cleaned.append("\uFFFD")
	return "".join(cleaned)


def summarize_tool_output(value: str, *, max_chars: int = 12000) -> str:
	sanitized = sanitize_text(value.rstrip())
	replacement_count = sanitized.count("\uFFFD")
	if replacement_count > 24:
		excerpt_lines = [line for line in sanitized.splitlines() if line.strip()]
		excerpt = "\n".join(excerpt_lines[:40]).replace("\uFFFD", "?").strip()
		note = f"[binary or control-heavy output omitted: {replacement_count} bytes sanitized]"
		return f"{note}\n\n{excerpt[:max_chars]}".strip()
	if len(sanitized) > max_chars:
		return f"{sanitized[:max_chars].rstrip()}\n\n[truncated at {max_chars} characters]"
	return sanitized


def preview_text(value: str, *, max_lines: int = 5, max_chars: int = 800) -> str:
	lines = value.splitlines()
	preview = "\n".join(lines[:max_lines]).strip()
	if len(preview) > max_chars:
		preview = preview[:max_chars].rstrip()
	if len(lines) > max_lines or len(value) > len(preview):
		return f"{preview}\n..."
	return preview


def extract_environment_info(message: str) -> tuple[str, str]:
	pattern = re.compile(r"\s*<environment_info>\n?(.*?)\n?</environment_info>\s*$", re.DOTALL)
	match = pattern.search(message)
	if not match:
		return message, ""
	main = message[: match.start()].rstrip()
	env = match.group(1).strip()
	return main, env


def render_environment_info(env_text: str) -> str:
	if not env_text:
		return ""
	escaped = html.escape(env_text)
	return f"<div>environment</div><pre>{escaped}</pre>"


def extract_shell_command(arguments: str, fallback_name: str) -> str:
	try:
		payload = json.loads(arguments)
	except json.JSONDecodeError:
		return fallback_name

	command = payload.get("cmd")
	if isinstance(command, str) and command.strip():
		return sanitize_text(command.strip())
	return fallback_name


def build_tool_meta(arguments: str, output: str) -> str:
	meta_parts: list[str] = []
	try:
		payload = json.loads(arguments)
	except json.JSONDecodeError:
		payload = {}

	for key in ("workdir", "max_output_tokens", "yield_time_ms"):
		value = payload.get(key)
		if value not in (None, "", []):
			meta_parts.append(f"{key}={value}")

	chunk_match = re.search(r"Chunk ID:\s*(.+)", output)
	wall_match = re.search(r"Wall time:\s*(.+)", output)
	exit_match = re.search(r"Process exited with code\s+(\d+)", output)
	token_match = re.search(r"Original token count:\s*(.+)", output)

	if chunk_match:
		meta_parts.append(f"chunk={chunk_match.group(1).strip()}")
	if wall_match:
		meta_parts.append(f"time={wall_match.group(1).strip()}")
	if exit_match:
		meta_parts.append(f"exit={exit_match.group(1)}")
	if token_match:
		meta_parts.append(f"tokens={token_match.group(1).strip()}")

	return " | ".join(meta_parts)


def extract_output_body(output: str) -> str:
	marker = "Output:\n"
	if marker in output:
		body = output.split(marker, 1)[1].strip()
		return body or "[no output]"
	return output.strip() or "[no output]"


def detect_output_tone(value: str) -> str:
	match = re.search(r"Process exited with code (\d+)", value)
	if match:
		return "success" if match.group(1) == "0" else "error"
	if "Successfully installed" in value or "Exported " in value:
		return "success"
	if "Traceback" in value or "fatal:" in value or "error" in value.lower():
		return "error"
	return "neutral"


def plain_message_from_content(content: list[dict[str, Any]]) -> str:
	chunks: list[str] = []
	for block in content:
		if block.get("type") in {"input_text", "output_text"}:
			text = block.get("text", "").strip()
			if text:
				chunks.append(text)
	return sanitize_text("\n\n".join(chunks).strip())


def build_markdown_renderer() -> MarkdownIt:
	return MarkdownIt("commonmark", {"html": False, "breaks": True}).enable("table")


def build_html_renderer() -> Environment:
	return Environment(autoescape=select_autoescape(["html", "xml"]))


def export_history(input_path: Path, output_path: Path, title_override: str | None) -> None:
	records = [json.loads(line) for line in input_path.read_text(encoding="utf-8").splitlines() if line.strip()]
	if not records:
		raise SystemExit("The input file is empty.")

	markdown = build_markdown_renderer()
	template_env = build_html_renderer()
	template = template_env.from_string(HTML_TEMPLATE)

	session_meta = next((record["payload"] for record in records if record["type"] == "session_meta"), {})
	turn_contexts: dict[str, dict[str, Any]] = {}
	turns_raw: list[dict[str, Any]] = []
	current_turn: dict[str, Any] | None = None
	pending_calls: dict[str, TimelineItem] = {}
	pending_call_args: dict[str, str] = {}
	counts: Counter[str] = Counter()

	for record in records:
		timestamp = record.get("timestamp")
		outer_type = record.get("type")

		if outer_type == "turn_context":
			payload = record["payload"]
			turn_contexts[payload["turn_id"]] = payload
			continue

		if outer_type == "session_meta":
			continue

		payload = record.get("payload", {})
		inner_type = payload.get("type")

		if inner_type == "task_started":
			turn_id = payload["turn_id"]
			current_turn = {
				"turn_id": turn_id,
				"started_at": timestamp,
				"items": [],
			}
			turns_raw.append(current_turn)
			counts["turns"] += 1
			continue

		if current_turn is None:
			continue

		if inner_type == "user_message":
			message, environment_info = extract_environment_info(
				sanitize_text(payload.get("message", "").strip())
			)
			item = TimelineItem(
				kind="user",
				badge="User",
				timestamp=compact_timestamp(timestamp),
				html=markdown.render(message) if message else "",
				meta_html=render_environment_info(environment_info),
			)
			current_turn["items"].append(item)
			counts["messages"] += 1
			continue

		if inner_type == "agent_message":
			item = TimelineItem(
				kind="assistant",
				badge="Assistant Update",
				timestamp=compact_timestamp(timestamp),
				html=markdown.render(sanitize_text(payload.get("message", "").strip())),
			)
			current_turn["items"].append(item)
			counts["messages"] += 1
			continue

		if inner_type == "function_call":
			command = extract_shell_command(
				payload.get("arguments", ""),
				payload.get("name", "unknown"),
			)
			item = TimelineItem(
				kind="tool",
				badge=command,
				timestamp=compact_timestamp(timestamp),
				html="",
				title_text=command,
				tone="neutral",
				meta_html="",
				tool_output="",
				details=[DetailBlock(title="tool", body="", tone="neutral")],
			)
			current_turn["items"].append(item)
			pending_calls[payload["call_id"]] = item
			pending_call_args[payload["call_id"]] = payload.get("arguments", "")
			counts["tool_calls"] += 1
			continue

		if inner_type == "function_call_output":
			call_id = payload.get("call_id")
			raw_output = payload.get("output", "")
			summarized_output = summarize_tool_output(raw_output)
			tone = detect_output_tone(raw_output)
			item = pending_calls.get(call_id)
			if item is not None:
				if tone != "neutral":
					item.tone = tone
				call_args = pending_call_args.get(call_id, "")
				item.meta_html = html.escape(build_tool_meta(call_args, summarized_output))
				item.tool_output = extract_output_body(summarized_output)
			else:
				current_turn["items"].append(
					TimelineItem(
						kind="tool",
						badge="shell output",
						timestamp=compact_timestamp(timestamp),
						title_text="shell output",
						tone=tone,
						meta_html=html.escape(build_tool_meta("", summarized_output)),
						tool_output=extract_output_body(summarized_output),
						details=[DetailBlock(title="tool", body="", tone=tone)],
					)
				)
			continue

		if inner_type == "task_complete":
			body = payload.get("last_agent_message", "").strip()
			body_sanitized = sanitize_text(body)
			if current_turn["items"]:
				last_item = current_turn["items"][-1]
				if (
					last_item.kind == "assistant"
					and last_item.badge == "Assistant Update"
					and last_item.html == (markdown.render(body_sanitized) if body_sanitized else "")
				):
					current_turn["items"].pop()
					counts["messages"] -= 1
			item = TimelineItem(
				kind="assistant",
				badge="Assistant Final",
				timestamp=compact_timestamp(timestamp),
				html=markdown.render(body_sanitized) if body_sanitized else "",
			)
			current_turn["items"].append(item)
			current_turn["completed_at"] = timestamp
			counts["messages"] += 1
			current_turn = None
			continue

		if inner_type == "reasoning":
			summary = payload.get("summary") or []
			if summary:
				current_turn["items"].append(
					TimelineItem(
						kind="system",
						badge="Reasoning Summary",
						timestamp=compact_timestamp(timestamp),
						html=markdown.render(
							sanitize_text("\n".join(f"- {line}" for line in summary))
						),
					)
				)
			continue

	rendered_turns: list[Turn] = []
	for index, turn in enumerate(turns_raw, start=1):
		turn_id = turn["turn_id"]
		context = turn_contexts.get(turn_id, {})
		started_at = format_timestamp(turn.get("started_at"))
		cwd = context.get("cwd", session_meta.get("cwd", ""))
		model = context.get("model", session_meta.get("model_provider", ""))
		heading = " | ".join(part for part in [started_at, model, cwd] if part)
		toc_label = started_at or turn_id
		rendered_turns.append(
			Turn(
				turn_id=turn_id,
				anchor=f"turn-{index}",
				heading=heading,
				toc_label=toc_label,
				item_count=len(turn["items"]),
				items=turn["items"],
			)
		)

	session_timestamp = parse_timestamp(session_meta.get("timestamp"))
	if session_timestamp is None and rendered_turns:
		session_timestamp = parse_timestamp(turns_raw[0].get("started_at"))

	document_title = title_override or f"Codex Export | {input_path.stem}"
	header_title = title_override or "Conversation History"
	subtitle_parts = [
		f"Model: {session_meta.get('model_provider', 'unknown')}",
		f"Origin: {session_meta.get('originator', 'unknown')}",
	]
	if session_meta.get("cwd"):
		subtitle_parts.append(f"CWD: {session_meta['cwd']}")
	header_subtitle = " | ".join(subtitle_parts)

	sidebar_rows = [
		{"key": "Session ID", "value": session_meta.get("id", "unknown")},
		{"key": "Started", "value": format_timestamp(session_meta.get("timestamp")) or "unknown"},
		{"key": "CLI Version", "value": session_meta.get("cli_version", "unknown")},
		{"key": "Source", "value": session_meta.get("source", "unknown")},
		{"key": "Provider", "value": session_meta.get("model_provider", "unknown")},
		{"key": "Working Directory", "value": session_meta.get("cwd", "unknown")},
	]

	stats = {
		"messages": counts["messages"],
		"tool_calls": counts["tool_calls"],
		"started_at": session_timestamp.astimezone().strftime("%b %d, %Y") if session_timestamp else "unknown",
	}

	rendered_html = template.render(
		document_title=document_title,
		header_title=header_title,
		header_subtitle=header_subtitle,
		turns=rendered_turns,
		sidebar_rows=sidebar_rows,
		stats=stats,
		source_name=input_path.name,
	)
	output_path.write_text(rendered_html, encoding="utf-8")


def main() -> None:
	args = parse_args()
	input_path = detect_input_file(args.input).resolve()
	if not input_path.exists():
		raise SystemExit(f"Input file does not exist: {input_path}")
	output_path = args.output.resolve() if args.output else input_path.with_suffix(".html")
	export_history(input_path=input_path, output_path=output_path, title_override=args.title)
	print(f"Exported {input_path.name} -> {output_path}")


if __name__ == "__main__":
	main()
