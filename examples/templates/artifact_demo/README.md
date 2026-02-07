# Artifact Demo Agent

This example agent demonstrates the **Hive Artifacts** feature - an interactive agent output protocol that allows agents to emit structured UI components.

## What it Does

The agent showcases two artifact types:

1. **Markdown Artifacts**: Display rich formatted content with headings, tables, and styling
2. **Form Artifacts**: Collect structured user input with various field types (text, select, checkbox)

## Flow

1. **Welcome**: Displays a markdown artifact with introduction
2. **Request Info**: Emits a form artifact asking for deployment configuration
3. **Process**: Receives form submission and processes it
4. **Results**: Shows formatted results in a markdown artifact

## Running the Agent

```bash
# Using TUI (recommended to see artifacts)
hive tui

# Then select "artifact_demo" from the list
```

## Artifact Protocol

Artifacts are emitted as JSON with the following structure:

```json
{
  "type": "artifact",
  "id": "unique-id",
  "component": "form" | "markdown",
  "props": { /* component-specific properties */ }
}
```

The TUI detects these JSON blocks and renders them as interactive widgets instead of plain text.

## Benefits

-  **Visual & Engaging**: Agents can create rich UIs on the fly
- ⚡ **Lightweight**: No servers, just JSON in logs
-  **Cloud-Native**: Works in headless environments (readable JSON) and interactive clients (rendered widgets)
-  **Autonomous**: Agent decides when to show UI

## Learn More

- See `core/framework/schemas/artifact.py` for schema definitions
- See `core/framework/tui/widgets/chat_repl.py` for TUI rendering logic
- See GitHub Issue #3914 for the full feature proposal
