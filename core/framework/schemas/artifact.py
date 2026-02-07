"""
Artifact Schema - Interactive Agent Output Protocol.

This module defines the schema for Hive Artifacts, a lightweight JSON-based
protocol that allows agents to emit interactive widgets (Forms, Charts, Mini-Apps)
directly into the output stream.

Key Concept: The agent emits a structured JSON block (the "Artifact") that
describes what to render. The client (TUI, Web, or IDE Extension) is responsible
for rendering it.

Benefits:
1. Visual & Engaging: Agents generate their own UI on the fly
2. Lightweight: No extra servers, ports, or state databases
3. Cloud-Native: In headless environments, the UI is just readable JSON logs
4. Autonomous: The agent decides when to show a UI
"""

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


class ArtifactType(StrEnum):
    """Types of interactive components an agent can emit."""

    FORM = "form"
    MARKDOWN = "markdown"
    CHART = "chart"  # Future: Phase 2
    CODE_SANDBOX = "code_sandbox"  # Future: Phase 3


class FormFieldType(StrEnum):
    """Types of form input fields."""

    TEXT = "text"
    SELECT = "select"
    CHECKBOX = "checkbox"
    TEXTAREA = "textarea"
    NUMBER = "number"


class FormField(BaseModel):
    """Definition of a single form field.

    Examples:
        Text input:
            FormField(name="username", type="text", label="Username", required=True)

        Select/dropdown:
            FormField(
                name="env",
                type="select",
                label="Environment",
                options=["staging", "production"],
                default="staging"
            )

        Checkbox:
            FormField(
                name="confirm",
                type="checkbox",
                label="I understand the risks"
            )
    """

    name: str = Field(description="Field identifier (used as key in response)")
    type: FormFieldType = Field(description="Type of input field")
    label: str = Field(description="Human-readable label")
    options: list[str] = Field(
        default_factory=list,
        description="Options for select fields (required if type=select)",
    )
    required: bool = Field(default=True, description="Whether field is required")
    default: str | int | bool | None = Field(
        default=None, description="Default value for the field"
    )
    placeholder: str | None = Field(
        default=None, description="Placeholder text for input fields"
    )
    help_text: str | None = Field(
        default=None, description="Additional help text for the field"
    )

    model_config = {"extra": "forbid"}


class FormComponent(BaseModel):
    """Interactive form for structured user input.

    The agent can emit a form to collect structured data from the user.
    When the user submits the form, the client sends the data back to the
    agent as a response.

    Example:
        ```python
        form = FormComponent(
            title="Confirm Deployment",
            description="Select deployment environment and confirm",
            fields=[
                FormField(
                    name="env",
                    type="select",
                    label="Environment",
                    options=["staging", "production"]
                ),
                FormField(
                    name="confirm",
                    type="checkbox",
                    label="I understand the risks"
                ),
            ],
            submit_label="Deploy Now"
        )
        ```

        User response:
        ```json
        {
            "env": "production",
            "confirm": true
        }
        ```
    """

    title: str = Field(description="Form title")
    description: str | None = Field(
        default=None, description="Optional form description"
    )
    fields: list[FormField] = Field(
        description="List of form fields", min_length=1
    )
    submit_label: str = Field(
        default="Submit", description="Label for submit button"
    )
    cancel_label: str | None = Field(
        default=None, description="Label for cancel button (if cancelable)"
    )

    model_config = {"extra": "forbid"}


class MarkdownComponent(BaseModel):
    """Rich text content using Markdown.

    The agent can emit markdown for formatted text output including:
    - Headings, lists, tables
    - Code blocks with syntax highlighting
    - Links, images, emphasis
    - Blockquotes, horizontal rules

    Example:
        ```python
        md = MarkdownComponent(
            content='''
# Analysis Results

The deployment was successful with the following metrics:

| Metric | Value |
|--------|-------|
| Uptime | 99.9% |
| Errors | 0     |

**Status**: ✓ All systems operational
            '''
        )
        ```
    """

    content: str = Field(description="Markdown-formatted text content")

    model_config = {"extra": "forbid"}


class ChartComponent(BaseModel):
    """Simple data visualization (Future: Phase 2).

    Placeholder for future chart support (Bar, Line, Pie charts).
    """

    chart_type: str = Field(description="Type of chart: bar, line, pie")
    data: dict[str, Any] = Field(description="Chart data")
    title: str | None = Field(default=None, description="Chart title")

    model_config = {"extra": "forbid"}


class CodeSandboxComponent(BaseModel):
    """Code snippet viewer/editor (Future: Phase 3).

    Placeholder for future code sandbox support.
    """

    code: str = Field(description="Code content")
    language: str = Field(description="Programming language")
    filename: str | None = Field(default=None, description="Optional filename")
    editable: bool = Field(default=False, description="Whether code is editable")

    model_config = {"extra": "forbid"}


class Artifact(BaseModel):
    """An interactive widget emitted by an agent.

    The agent emits artifacts as structured JSON to stdout. The client
    (TUI, Web, IDE) detects artifacts by the `type: "artifact"` field
    and renders them appropriately.

    The "UI is in the Logs" concept: Since the UI definition is stateless
    JSON, you can "replay" an interaction just by reading the logs.

    Example JSON output:
        ```json
        {
            "type": "artifact",
            "id": "deployment-form-01",
            "component": "form",
            "props": {
                "title": "Confirm Deployment",
                "fields": [
                    {
                        "name": "env",
                        "type": "select",
                        "label": "Environment",
                        "options": ["staging", "prod"]
                    }
                ]
            }
        }
        ```

    Client Response (when user interacts):
        ```json
        {
            "artifact_id": "deployment-form-01",
            "action": "submit",
            "data": {
                "env": "prod"
            }
        }
        ```
    """

    type: Literal["artifact"] = Field(
        default="artifact",
        description="Must be 'artifact' for detection by clients",
    )
    id: str = Field(
        description="Unique identifier for this artifact instance"
    )
    component: ArtifactType = Field(
        description="Type of component to render"
    )
    props: FormComponent | MarkdownComponent | ChartComponent | CodeSandboxComponent = Field(
        description="Component-specific properties",
        discriminator="__artifact_component_type__",  # Will be set by component type
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When this artifact was emitted",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata for client use",
    )

    model_config = {"extra": "forbid"}

    @classmethod
    def create_form(
        cls,
        id: str,
        title: str,
        fields: list[FormField],
        description: str | None = None,
        submit_label: str = "Submit",
    ) -> "Artifact":
        """Convenience method to create a form artifact.

        Example:
            ```python
            artifact = Artifact.create_form(
                id="deploy-form",
                title="Deploy Application",
                fields=[
                    FormField(name="env", type="select", label="Environment",
                              options=["staging", "prod"]),
                ],
                submit_label="Deploy Now"
            )
            print(artifact.model_dump_json())  # Emit to stdout
            ```
        """
        return cls(
            id=id,
            component=ArtifactType.FORM,
            props=FormComponent(
                title=title,
                description=description,
                fields=fields,
                submit_label=submit_label,
            ),
        )

    @classmethod
    def create_markdown(
        cls,
        id: str,
        content: str,
    ) -> "Artifact":
        """Convenience method to create a markdown artifact.

        Example:
            ```python
            artifact = Artifact.create_markdown(
                id="report-md",
                content="# Report\\n\\nAnalysis complete."
            )
            print(artifact.model_dump_json())  # Emit to stdout
            ```
        """
        return cls(
            id=id,
            component=ArtifactType.MARKDOWN,
            props=MarkdownComponent(content=content),
        )


class ArtifactResponse(BaseModel):
    """User response to an artifact interaction.

    When a user interacts with an artifact (e.g., submits a form),
    the client sends this response back to the agent.
    """

    artifact_id: str = Field(description="ID of the artifact being responded to")
    action: str = Field(
        description="Action taken: 'submit', 'cancel', 'edit', etc."
    )
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="User-provided data (e.g., form field values)",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the response was generated",
    )

    model_config = {"extra": "forbid"}
