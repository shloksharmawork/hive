"""
Artifact Demo Agent - Demonstrates Hive Artifacts feature.

This agent showcases the interactive agent output protocol by emitting
form and markdown artifacts instead of plain text.
"""

import json
from datetime import datetime

from framework.graph import GraphSpec, Edge, EventLoopNode
from framework.goal import Goal
from framework.schemas.artifact import Artifact, FormField, FormFieldType


# ============================================================================
# Goal Definition
# ============================================================================

goal = Goal(
    name="Artifact Demo",
    description="Demonstrate Hive Artifacts with interactive forms and markdown output",
    success_criteria=[
        "Agent emits a form artifact for user input",
        "Agent receives and processes form submission",
        "Agent emits a markdown artifact with formatted results",
    ],
    constraints=[
        "Use Hive Artifacts protocol (JSON with type='artifact')",
        "Support both form and markdown components",
    ],
)


# ============================================================================
# Node Definitions
# ============================================================================

welcome_node = EventLoopNode(
    id="welcome",
    name="Welcome Message",
    description="Show welcome message with markdown artifact",
    input_keys=["user_input"],
    output_keys=["welcome_message"],
    client_facing=False,
)

request_deployment_info = EventLoopNode(
    id="request_deployment",
    name="Request Deployment Information",
    description="Emit a form artifact to collect deployment details from user",
    input_keys=["welcome_message"],
    output_keys=["deployment_form"],
    client_facing=False,
)

process_deployment = EventLoopNode(
    id="process_deployment",
    name="Process Deployment",
    description="Process the deployment form submission and emit confirmation",
    input_keys=["deployment_form", "user_response"],
    output_keys=["deployment_result"],
    client_facing=True,  # Waits for user input (form submission)
)

show_results = EventLoopNode(
    id="show_results",
    name="Show Results",
    description="Display deployment results using markdown artifact",
    input_keys=["deployment_result"],
    output_keys=["final_report"],
    client_facing=False,
)


# ============================================================================
# Graph Structure
# ============================================================================

nodes = [
    welcome_node,
    request_deployment_info,
    process_deployment,
    show_results,
]

edges = [
    Edge(from_node="welcome", to_node="request_deployment"),
    Edge(from_node="request_deployment", to_node="process_deployment"),
    Edge(from_node="process_deployment", to_node="show_results"),
]

graph = GraphSpec(
    name="artifact_demo",
    description="Demo agent for Hive Artifacts",
    nodes=nodes,
    edges=edges,
    entry_node="welcome",
    terminal_nodes=["show_results"],
)


# ============================================================================
# Node Implementations
# ============================================================================


async def execute_welcome(context: dict) -> dict:
    """Show welcome message with markdown artifact."""

    welcome_md = """
# 🎯 Hive Artifacts Demo

Welcome to the **Hive Artifacts** demonstration!

This agent will showcase the new interactive output protocol by:

1. Displaying this **Markdown** artifact
2. Emitting a **Form** artifact for you to fill out
3. Processing your submission
4. Showing formatted results

Let's get started! 👇
"""

    artifact = Artifact.create_markdown(
        id="welcome-md-001",
        content=welcome_md,
    )

    # Emit artifact as JSON
    artifact_json = artifact.model_dump_json()

    return {
        "welcome_message": artifact_json,
        "output_string": artifact_json,
    }


async def execute_request_deployment(context: dict) -> dict:
    """Emit a form artifact to collect deployment information."""

    artifact = Artifact.create_form(
        id="deployment-form-001",
        title="Deployment Configuration",
        description="Please configure your deployment settings below:",
        fields=[
            FormField(
                name="environment",
                type=FormFieldType.SELECT,
                label="Target Environment",
                options=["development", "staging", "production"],
                default="staging",
                required=True,
                help_text="Select the environment to deploy to",
            ),
            FormField(
                name="branch",
                type=FormFieldType.TEXT,
                label="Git Branch",
                default="main",
                required=True,
                placeholder="e.g., main, develop, feature/xyz",
            ),
            FormField(
                name="run_tests",
                type=FormFieldType.CHECKBOX,
                label="Run tests before deployment",
                default=True,
                required=False,
            ),
            FormField(
                name="confirm",
                type=FormFieldType.CHECKBOX,
                label="I understand this will deploy to the selected environment",
                required=True,
            ),
        ],
        submit_label="Deploy Now",
    )

    artifact_json = artifact.model_dump_json()

    return {
        "deployment_form": artifact_json,
        "output_string": artifact_json,
    }


async def execute_process_deployment(context: dict) -> dict:
    """Process the deployment form submission."""

    # In a real agent, user_response would contain the form data
    # For this demo, we simulate processing

    user_response = context.get("user_input", "{}")

    try:
        form_data = (
            json.loads(user_response)
            if isinstance(user_response, str)
            else user_response
        )
    except json.JSONDecodeError:
        form_data = {
            "environment": "staging",
            "branch": "main",
            "run_tests": True,
            "confirm": True,
        }

    # Simulate deployment
    deployment_info = {
        "environment": form_data.get("environment", "staging"),
        "branch": form_data.get("branch", "main"),
        "run_tests": form_data.get("run_tests", True),
        "timestamp": datetime.now().isoformat(),
        "status": "success",
    }

    return {
        "deployment_result": json.dumps(deployment_info),
        "output_string": "Processing deployment...",
    }


async def execute_show_results(context: dict) -> dict:
    """Display deployment results using markdown artifact."""

    deployment_result = context.get("deployment_result", "{}")

    try:
        result_data = (
            json.loads(deployment_result)
            if isinstance(deployment_result, str)
            else deployment_result
        )
    except json.JSONDecodeError:
        result_data = {"status": "unknown"}

    results_md = f"""
# ✅ Deployment Complete

Your deployment has been successfully completed!

## Deployment Summary

| Parameter | Value |
|-----------|-------|
| Environment | **{result_data.get("environment", "N/A")}** |
| Branch | `{result_data.get("branch", "N/A")}` |
| Tests Run | {"Yes ✓" if result_data.get("run_tests") else "No ✗"} |
| Status | **{result_data.get("status", "unknown").upper()}** |
| Timestamp | {result_data.get("timestamp", "N/A")} |

---

## Next Steps

1. Monitor the deployment logs
2. Verify application health checks
3. Test critical user flows
4. Roll back if any issues detected

**Thank you for using Hive Artifacts!** 🚀
"""

    artifact = Artifact.create_markdown(
        id="results-md-001",
        content=results_md,
    )

    artifact_json = artifact.model_dump_json()

    return {
        "final_report": artifact_json,
        "output_string": artifact_json,
    }


# Register node executors
welcome_node.executor = execute_welcome
request_deployment_info.executor = execute_request_deployment
process_deployment.executor = execute_process_deployment
show_results.executor = execute_show_results


# ============================================================================
# Entry Points
# ============================================================================

# Standard entry point for conversation-style interaction
entry_points = [
    {
        "id": "main",
        "entry_node": "welcome",
        "description": "Main entry point - demonstrates artifact protocol",
    }
]
