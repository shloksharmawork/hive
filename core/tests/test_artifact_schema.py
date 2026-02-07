"""Tests for artifact schema validation and serialization."""

import json
from datetime import datetime

import pytest

from framework.schemas.artifact import (
    Artifact,
    ArtifactResponse,
    ArtifactType,
    FormComponent,
    FormField,
    FormFieldType,
    MarkdownComponent,
)


class TestFormField:
    """Test FormField validation."""

    def test_create_text_field(self):
        """Test creating a text input field."""
        field = FormField(
            name="username",
            type=FormFieldType.TEXT,
            label="Username",
            required=True,
            placeholder="Enter your username",
        )
        assert field.name == "username"
        assert field.type == FormFieldType.TEXT
        assert field.required is True
        assert field.placeholder == "Enter your username"

    def test_create_select_field(self):
        """Test creating a select/dropdown field."""
        field = FormField(
            name="environment",
            type=FormFieldType.SELECT,
            label="Environment",
            options=["staging", "production"],
            default="staging",
        )
        assert field.name == "environment"
        assert field.type == FormFieldType.SELECT
        assert field.options == ["staging", "production"]
        assert field.default == "staging"

    def test_create_checkbox_field(self):
        """Test creating a checkbox field."""
        field = FormField(
            name="confirm",
            type=FormFieldType.CHECKBOX,
            label="I agree to terms",
            default=False,
        )
        assert field.name == "confirm"
        assert field.type == FormFieldType.CHECKBOX
        assert field.default is False

    def test_field_defaults(self):
        """Test default values for optional fields."""
        field = FormField(
            name="test",
            type=FormFieldType.TEXT,
            label="Test",
        )
        assert field.required is True  # Default
        assert field.default is None
        assert field.placeholder is None
        assert field.help_text is None
        assert field.options == []

    def test_field_json_serialization(self):
        """Test JSON serialization of FormField."""
        field = FormField(
            name="env",
            type=FormFieldType.SELECT,
            label="Environment",
            options=["dev", "prod"],
        )
        json_data = field.model_dump()
        assert json_data["name"] == "env"
        assert json_data["type"] == "select"
        assert json_data["options"] == ["dev", "prod"]


class TestFormComponent:
    """Test FormComponent validation."""

    def test_create_basic_form(self):
        """Test creating a basic form."""
        form = FormComponent(
            title="User Registration",
            fields=[
                FormField(name="name", type=FormFieldType.TEXT, label="Name"),
                FormField(name="email", type=FormFieldType.TEXT, label="Email"),
            ],
        )
        assert form.title == "User Registration"
        assert len(form.fields) == 2
        assert form.submit_label == "Submit"  # Default

    def test_form_with_description(self):
        """Test form with description."""
        form = FormComponent(
            title="Deploy App",
            description="Select environment and confirm deployment",
            fields=[
                FormField(
                    name="env",
                    type=FormFieldType.SELECT,
                    label="Environment",
                    options=["staging", "prod"],
                ),
            ],
            submit_label="Deploy Now",
        )
        assert form.description == "Select environment and confirm deployment"
        assert form.submit_label == "Deploy Now"

    def test_form_requires_fields(self):
        """Test that form requires at least one field."""
        with pytest.raises(ValueError):
            FormComponent(title="Empty Form", fields=[])

    def test_form_json_serialization(self):
        """Test JSON serialization of FormComponent."""
        form = FormComponent(
            title="Test Form",
            fields=[
                FormField(name="field1", type=FormFieldType.TEXT, label="Field 1"),
            ],
        )
        json_data = form.model_dump()
        assert json_data["title"] == "Test Form"
        assert len(json_data["fields"]) == 1


class TestMarkdownComponent:
    """Test MarkdownComponent validation."""

    def test_create_markdown(self):
        """Test creating a markdown component."""
        md = MarkdownComponent(content="# Hello World\n\nThis is **bold** text.")
        assert "# Hello World" in md.content
        assert "**bold**" in md.content

    def test_markdown_with_code_block(self):
        """Test markdown with code blocks."""
        md = MarkdownComponent(
            content="""
# Code Example

```python
def hello():
    print("Hello, World!")
```
"""
        )
        assert "```python" in md.content

    def test_markdown_json_serialization(self):
        """Test JSON serialization of MarkdownComponent."""
        md = MarkdownComponent(content="# Test")
        json_data = md.model_dump()
        assert json_data["content"] == "# Test"


class TestArtifact:
    """Test Artifact model."""

    def test_create_form_artifact(self):
        """Test creating a form artifact."""
        artifact = Artifact(
            id="form-001",
            component=ArtifactType.FORM,
            props=FormComponent(
                title="Test Form",
                fields=[
                    FormField(name="test", type=FormFieldType.TEXT, label="Test"),
                ],
            ),
        )
        assert artifact.type == "artifact"
        assert artifact.id == "form-001"
        assert artifact.component == ArtifactType.FORM
        assert isinstance(artifact.props, FormComponent)

    def test_create_markdown_artifact(self):
        """Test creating a markdown artifact."""
        artifact = Artifact(
            id="md-001",
            component=ArtifactType.MARKDOWN,
            props=MarkdownComponent(content="# Test"),
        )
        assert artifact.id == "md-001"
        assert artifact.component == ArtifactType.MARKDOWN
        assert isinstance(artifact.props, MarkdownComponent)

    def test_artifact_has_timestamp(self):
        """Test that artifact has a timestamp."""
        artifact = Artifact(
            id="test",
            component=ArtifactType.MARKDOWN,
            props=MarkdownComponent(content="test"),
        )
        assert isinstance(artifact.timestamp, datetime)

    def test_artifact_json_serialization(self):
        """Test full JSON serialization of artifact."""
        artifact = Artifact(
            id="deploy-form",
            component=ArtifactType.FORM,
            props=FormComponent(
                title="Deploy",
                fields=[
                    FormField(
                        name="env",
                        type=FormFieldType.SELECT,
                        label="Environment",
                        options=["staging", "prod"],
                    ),
                ],
            ),
        )

        # Test model_dump (dict)
        data = artifact.model_dump()
        assert data["type"] == "artifact"
        assert data["id"] == "deploy-form"
        assert data["component"] == "form"
        assert "props" in data

        # Test model_dump_json (JSON string)
        json_str = artifact.model_dump_json()
        parsed = json.loads(json_str)
        assert parsed["type"] == "artifact"
        assert parsed["component"] == "form"

    def test_artifact_json_deserialization(self):
        """Test parsing artifact from JSON."""
        json_data = {
            "type": "artifact",
            "id": "test-form",
            "component": "form",
            "props": {
                "title": "Test",
                "fields": [
                    {
                        "name": "field1",
                        "type": "text",
                        "label": "Field 1",
                        "options": [],
                        "required": True,
                        "default": None,
                        "placeholder": None,
                        "help_text": None,
                    }
                ],
                "description": None,
                "submit_label": "Submit",
                "cancel_label": None,
            },
            "timestamp": "2026-02-07T16:00:00",
            "metadata": {},
        }

        artifact = Artifact.model_validate(json_data)
        assert artifact.id == "test-form"
        assert artifact.component == ArtifactType.FORM

    def test_create_form_convenience_method(self):
        """Test Artifact.create_form() convenience method."""
        artifact = Artifact.create_form(
            id="quick-form",
            title="Quick Form",
            fields=[
                FormField(name="name", type=FormFieldType.TEXT, label="Name"),
            ],
            submit_label="Go",
        )
        assert artifact.id == "quick-form"
        assert artifact.component == ArtifactType.FORM
        assert isinstance(artifact.props, FormComponent)
        assert artifact.props.title == "Quick Form"
        assert artifact.props.submit_label == "Go"

    def test_create_markdown_convenience_method(self):
        """Test Artifact.create_markdown() convenience method."""
        artifact = Artifact.create_markdown(
            id="quick-md",
            content="# Quick Markdown",
        )
        assert artifact.id == "quick-md"
        assert artifact.component == ArtifactType.MARKDOWN
        assert isinstance(artifact.props, MarkdownComponent)
        assert artifact.props.content == "# Quick Markdown"


class TestArtifactResponse:
    """Test ArtifactResponse model."""

    def test_create_submit_response(self):
        """Test creating a form submission response."""
        response = ArtifactResponse(
            artifact_id="form-001",
            action="submit",
            data={"env": "production", "confirm": True},
        )
        assert response.artifact_id == "form-001"
        assert response.action == "submit"
        assert response.data["env"] == "production"
        assert response.data["confirm"] is True

    def test_create_cancel_response(self):
        """Test creating a cancel response."""
        response = ArtifactResponse(
            artifact_id="form-001",
            action="cancel",
            data={},
        )
        assert response.action == "cancel"
        assert response.data == {}

    def test_response_json_serialization(self):
        """Test JSON serialization of response."""
        response = ArtifactResponse(
            artifact_id="test",
            action="submit",
            data={"key": "value"},
        )
        json_data = response.model_dump()
        assert json_data["artifact_id"] == "test"
        assert json_data["action"] == "submit"
        assert json_data["data"]["key"] == "value"


class TestArtifactExamples:
    """Test real-world artifact examples from the issue."""

    def test_deployment_form_example(self):
        """
        Test the deployment form example from issue #3914.

        Example from issue:
        {
          "type": "artifact",
          "id": "deployment-form-01",
          "component": "form",
          "props": {
            "title": "Confirm Deployment",
            "fields": [
              {"name": "env", "type": "select", "options": ["staging", "prod"]},
              {"name": "confirm", "type": "checkbox", "label": "I understand the risks"}
            ]
          }
        }
        """
        artifact = Artifact.create_form(
            id="deployment-form-01",
            title="Confirm Deployment",
            fields=[
                FormField(
                    name="env",
                    type=FormFieldType.SELECT,
                    label="Environment",
                    options=["staging", "prod"],
                ),
                FormField(
                    name="confirm",
                    type=FormFieldType.CHECKBOX,
                    label="I understand the risks",
                ),
            ],
        )

        # Verify structure
        assert artifact.id == "deployment-form-01"
        json_str = artifact.model_dump_json()
        parsed = json.loads(json_str)

        assert parsed["type"] == "artifact"
        assert parsed["component"] == "form"
        assert len(parsed["props"]["fields"]) == 2
        assert parsed["props"]["fields"][0]["name"] == "env"
        assert parsed["props"]["fields"][1]["name"] == "confirm"

    def test_analysis_report_markdown(self):
        """Test creating an analysis report with markdown."""
        report = """
# Analysis Results

The deployment was successful with the following metrics:

| Metric | Value |
|--------|-------|
| Uptime | 99.9% |
| Errors | 0     |

**Status**: ✓ All systems operational
"""
        artifact = Artifact.create_markdown(
            id="report-001",
            content=report,
        )

        assert "Analysis Results" in artifact.props.content
        assert "99.9%" in artifact.props.content
        json_str = artifact.model_dump_json()
        assert "Analysis Results" in json_str
