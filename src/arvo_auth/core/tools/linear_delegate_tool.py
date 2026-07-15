"""Delegate Linear issue operations to Claude Code CLI (Linear MCP)."""

from __future__ import annotations

import os
from typing import Literal, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from arvo_auth.core.linear_project_ref import LinearProjectRef
from arvo_auth.core.tools.notion_claude_delegate import run_claude_code_print

LinearOperation = Literal["create_issue", "get_team", "list_labels", "get_project"]


def _linear_timeout() -> int:
    return int(os.getenv("ARVO_LINEAR_DELEGATE_TIMEOUT_SEC", "180"))


class LinearDelegateInput(BaseModel):
    operation: LinearOperation = Field(
        ...,
        description=(
            "Operation: create_issue (create one issue, returns its Linear ID like TEA-42), "
            "get_team (verify team exists, returns team ID), "
            "list_labels (list available label names for the team)."
        ),
    )
    team_key: str = Field(
        default="",
        description="Linear team key (e.g. NEW, TEA, COP). Required for all operations.",
    )
    title: str = Field(
        default="",
        description="Issue title. Required for create_issue.",
    )
    description: str = Field(
        default="",
        description=(
            "Full markdown description. Required for create_issue. "
            "Include all template sections verbatim (Objetivo, Contexto mínimo, "
            "Contrato de API, Regras técnicas, Critérios de aceite, Fora de escopo, "
            "Referência no SRS) as applicable."
        ),
    )
    labels: list[str] = Field(
        default_factory=list,
        description="Label names to attach (e.g. ['Backend', 'Feature', 'Modulo-Dashboard']).",
    )
    priority: int = Field(
        default=0,
        ge=0,
        le=4,
        description="1=Urgent 2=High 3=Medium 4=Low 0=unset.",
    )
    estimate: int = Field(
        default=0,
        ge=0,
        le=13,
        description=(
            "Story points in Fibonacci scale (2, 3, 5, 8, 13). "
            "0=unset (use for Issue Pai). Max allowed by rules: 5."
        ),
    )
    parent_id: str = Field(
        default="",
        description=(
            "Real Linear ID of parent issue (e.g. TEA-42). "
            "Must be a real ID — never a tempId. Leave empty for Issue Pai."
        ),
    )
    blocked_by: list[str] = Field(
        default_factory=list,
        description=(
            "Real Linear IDs this issue is blocked by (e.g. ['TEA-43', 'TEA-44']). "
            "Must be real IDs — resolve all tempIds before calling."
        ),
    )
    project_url: str = Field(
        default="",
        description=(
            "Full Linear project URL (preferred), e.g. "
            "https://linear.app/workspace/project/my-project-1bb8bb27c4d5. Optional."
        ),
    )


class LinearDelegateTool(BaseTool):
    name: str = "linear_issue_manager"
    description: str = (
        "Create and query Linear issues via Linear MCP (delegates to Claude Code CLI). "
        "Operations: "
        "create_issue — create one issue and return its real Linear ID (e.g. TEA-42); "
        "get_team — verify a team key exists and return its UUID; "
        "list_labels — list available label names for a team; "
        "get_project — verify a Linear project exists for a team and return its UUID. "
        "Always create Issue Pai before its sub-issues. "
        "Resolve all tempId references to real Linear IDs before passing parent_id or blocked_by."
    )
    args_schema: Type[BaseModel] = LinearDelegateInput

    def _run(
        self,
        operation: str,
        team_key: str = "",
        title: str = "",
        description: str = "",
        labels: list[str] | None = None,
        priority: int = 0,
        estimate: int = 0,
        parent_id: str = "",
        blocked_by: list[str] | None = None,
        project_url: str = "",
    ) -> str:
        op = operation.strip().lower()
        team = team_key.strip()
        project_ref = self._resolve_project_ref(project_url)

        if op == "get_team":
            return self._get_team(team)
        if op == "list_labels":
            return self._list_labels(team)
        if op == "get_project":
            return self._get_project(team_key=team, project_ref=project_ref)
        if op == "create_issue":
            return self._create_issue(
                team_key=team,
                title=title,
                description=description,
                labels=labels or [],
                priority=priority,
                estimate=estimate,
                parent_id=parent_id,
                blocked_by=blocked_by or [],
                project_ref=project_ref,
            )
        return (
            f"ERROR: unknown operation {operation!r}. "
            "Use create_issue, get_team, list_labels, or get_project."
        )

    def _get_team(self, team_key: str) -> str:
        if not team_key:
            return "ERROR: team_key is required for get_team."
        prompt = (
            "You have access to Linear through MCP.\n"
            f"Find the Linear team with key '{team_key}'.\n"
            "Output rules:\n"
            "- Return ONLY the team UUID on a single line, e.g.: 7f3a1b2c-...\n"
            f"- If not found, return: ERROR: Team '{team_key}' not found.\n"
            "- No markdown, no JSON wrapper, no explanation."
        )
        return run_claude_code_print(prompt, timeout_sec=_linear_timeout())

    def _list_labels(self, team_key: str) -> str:
        if not team_key:
            return "ERROR: team_key is required for list_labels."
        prompt = (
            "You have access to Linear through MCP.\n"
            f"List all issue labels for the Linear team with key '{team_key}'.\n"
            "Output rules:\n"
            "- Return ONLY a comma-separated list of label names, e.g.: Backend, Frontend, Feature\n"
            "- No markdown, no JSON, no explanation."
        )
        return run_claude_code_print(prompt, timeout_sec=_linear_timeout())

    @staticmethod
    def _resolve_project_ref(project_url: str) -> LinearProjectRef | None:
        raw = project_url.strip()
        if not raw:
            return None
        ref, err = LinearProjectRef.from_url_or_legacy(raw)
        if err or not ref or not ref.is_configured():
            return None
        return ref

    def _get_project(
        self,
        team_key: str,
        project_ref: LinearProjectRef | None,
    ) -> str:
        if not team_key:
            return "ERROR: team_key is required for get_project."
        if not project_ref or not project_ref.is_configured():
            return "ERROR: project_url is required for get_project."

        hint = project_ref.prompt_hint()
        prompt = (
            "You have access to Linear through MCP.\n"
            f"Find the Linear project for team '{team_key}' using this reference: {hint}\n"
            "When a URL is provided, open that exact project page.\n"
            "Output rules:\n"
            "- Return ONLY the project UUID on a single line, e.g.: 7f3a1b2c-...\n"
            f"- If not found, return: ERROR: Project not found for team '{team_key}' ({hint}).\n"
            "- No markdown, no JSON wrapper, no explanation."
        )
        return run_claude_code_print(prompt, timeout_sec=_linear_timeout())

    def _create_issue(
        self,
        team_key: str,
        title: str,
        description: str,
        labels: list[str],
        priority: int,
        estimate: int,
        parent_id: str,
        blocked_by: list[str],
        project_ref: LinearProjectRef | None,
    ) -> str:
        if not team_key:
            return "ERROR: team_key is required for create_issue."
        if not title.strip():
            return "ERROR: title is required for create_issue."

        priority_map = {1: "Urgent", 2: "High", 3: "Medium", 4: "Low"}
        lines = [
            "You have access to Linear through MCP.",
            f"Create one Linear issue for team '{team_key}' with the following fields:",
            "",
            f"Title: {title}",
        ]
        if labels:
            lines.append(f"Labels: {', '.join(labels)}")
        if priority:
            lines.append(f"Priority: {priority} ({priority_map.get(priority, str(priority))})")
        if estimate:
            lines.append(f"Estimate: {estimate} story points")
        if parent_id.strip():
            lines.append(f"Parent issue ID: {parent_id.strip()}")
        if blocked_by:
            lines.append(f"Blocked by (add as blocking relations): {', '.join(blocked_by)}")
        if project_ref and project_ref.is_configured():
            lines.append(f"Linear project: {project_ref.prompt_hint()}")
        lines += [
            "",
            "Full description (use verbatim — do not summarize or truncate):",
            description,
            "",
            "Steps:",
            "1. Use list_teams or get_team MCP tool to resolve the team key to its UUID.",
            "2. When a Linear project URL or reference is specified, resolve it to a project",
            "   UUID (open the URL or search projects for the team). Include projectId in save_issue.",
            "3. If labels are specified, use list_issue_labels to get existing label IDs.",
            "   Create any missing labels with create_issue_label before creating the issue.",
            "4. Call save_issue with title, description, teamId, labelIds, priority, estimate.",
            "5. If parent_id is provided, include it as parentId in save_issue.",
            "6. If blocked_by has IDs, add blocking relations after issue creation if the",
            "   save_issue tool does not support them directly.",
            "",
            "Output rules:",
            "- Return ONLY the created issue identifier on a single line, e.g.: TEA-42",
            "- No markdown, no JSON wrapper, no explanation.",
            "- If creation fails, return: ERROR: <reason>",
        ]
        prompt = "\n".join(lines)
        return run_claude_code_print(prompt, timeout_sec=_linear_timeout()).strip()
