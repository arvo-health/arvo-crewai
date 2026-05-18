"""Read-only GitHub queries via the official GitHub CLI (`gh`)."""

from __future__ import annotations

import re
from typing import Literal, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from arvo_auth.core.tools.github_cli_common import format_json_output, run_gh

GhOperation = Literal[
    "pr_list",
    "pr_view",
    "pr_checks",
    "issue_list",
    "issue_view",
    "run_list",
    "run_view",
    "repo_view",
    "branch_compare",
    "api_get",
]

_BRANCH_PATTERN = re.compile(r"^[A-Za-z0-9_../-]+$")

_REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_API_ENDPOINT_PATTERN = re.compile(r"^/[A-Za-z0-9_./{}%-]+$")


class GitHubCliInput(BaseModel):
    operation: GhOperation = Field(
        ...,
        description=(
            "Query type: pr_list, pr_view, pr_checks, issue_list, issue_view, "
            "run_list, run_view, repo_view, branch_compare (diff base...head), "
            "or api_get (GitHub REST via `gh api`)."
        ),
    )
    repo: str = Field(
        default="",
        description=(
            "Repository as owner/name (e.g. org/arvo-auth). "
            "Empty uses the current directory repo or GH_REPO."
        ),
    )
    number: int = Field(
        default=0,
        ge=0,
        description="PR, issue, or workflow run number (required for *_view and run_view).",
    )
    state: str = Field(
        default="open",
        description="For pr_list / issue_list: open, closed, merged (PR only), or all.",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Max rows for list operations (1–100).",
    )
    search: str = Field(
        default="",
        description="Optional GitHub search/filter string for pr_list or issue_list.",
    )
    branch: str = Field(
        default="",
        description="Optional branch name for pr_list (--head) or run_list (--branch).",
    )
    base_branch: str = Field(
        default="",
        description=(
            "For branch_compare: origin/base branch (e.g. dev). "
            "Compare ref is base_branch...head_branch."
        ),
    )
    head_branch: str = Field(
        default="",
        description="For branch_compare: feature/new branch (e.g. TEA-M1).",
    )
    endpoint: str = Field(
        default="",
        description=(
            "For api_get only: REST path starting with /, e.g. "
            "/repos/{owner}/{repo}/pulls/42 or /repos/{owner}/{repo}/actions/runs."
        ),
    )


class GitHubCliTool(BaseTool):
    name: str = "github_cli_query"
    description: str = (
        "Query GitHub using the authenticated `gh` CLI (read-only). "
        "Use for pull requests, issues, Actions workflow runs, repository metadata, "
        "branch diffs (branch_compare with base_branch and head_branch), or custom GET "
        "requests via `gh api`. Requires `gh auth login` on the host. "
        "Set repo to owner/name when not running inside the target repository."
    )
    args_schema: Type[BaseModel] = GitHubCliInput

    def _run(
        self,
        operation: str,
        repo: str = "",
        number: int = 0,
        state: str = "open",
        limit: int = 10,
        search: str = "",
        branch: str = "",
        base_branch: str = "",
        head_branch: str = "",
        endpoint: str = "",
    ) -> str:
        op = operation.strip().lower()
        repo_arg = self._normalize_repo(repo)
        if isinstance(repo_arg, str) and repo_arg.startswith("ERROR"):
            return repo_arg

        handlers = {
            "pr_list": lambda: self._pr_list(repo_arg, state, limit, search, branch),
            "pr_view": lambda: self._pr_view(repo_arg, number),
            "pr_checks": lambda: self._pr_checks(repo_arg, number),
            "issue_list": lambda: self._issue_list(repo_arg, state, limit, search),
            "issue_view": lambda: self._issue_view(repo_arg, number),
            "run_list": lambda: self._run_list(repo_arg, limit, branch),
            "run_view": lambda: self._run_view(repo_arg, number),
            "repo_view": lambda: self._repo_view(repo_arg),
            "branch_compare": lambda: self._branch_compare(
                repo_arg, base_branch, head_branch
            ),
            "api_get": lambda: self._api_get(repo_arg, endpoint),
        }

        if op not in handlers:
            return (
                f"ERROR: unknown operation {operation!r}. "
                f"Use one of: {', '.join(sorted(handlers))}."
            )

        raw = handlers[op]()
        if raw.startswith("ERROR:") or raw.startswith("(no output)"):
            return raw
        if raw.lstrip().startswith(("{", "[")):
            return format_json_output(raw)
        return raw

    @staticmethod
    def _normalize_repo(repo: str) -> str | None:
        cleaned = repo.strip()
        if not cleaned:
            return None
        if not _REPO_PATTERN.match(cleaned):
            return "ERROR: repo must be owner/name (e.g. my-org/arvo-auth)."
        return cleaned

    @staticmethod
    def _require_number(number: int, label: str) -> str | None:
        if number < 1:
            return f"ERROR: {label} requires a positive number."
        return None

    def _pr_list(
        self,
        repo: str | None,
        state: str,
        limit: int,
        search: str,
        branch: str,
    ) -> str:
        args = [
            "pr",
            "list",
            "--limit",
            str(limit),
            "--json",
            "number,title,state,url,author,headRefName,baseRefName,updatedAt",
        ]
        st = state.strip().lower()
        if st in ("open", "closed", "merged", "all"):
            args.extend(["--state", st])
        if search.strip():
            args.extend(["--search", search.strip()])
        if branch.strip():
            args.extend(["--head", branch.strip()])
        return run_gh(args, repo=repo)

    def _pr_view(self, repo: str | None, number: int) -> str:
        err = self._require_number(number, "pr_view")
        if err:
            return err
        return run_gh(
            [
                "pr",
                "view",
                str(number),
                "--json",
                "number,title,body,state,url,author,baseRefName,headRefName,"
                "commits,files,additions,deletions,changedFiles,reviews,statusCheckRollup",
            ],
            repo=repo,
        )

    def _pr_checks(self, repo: str | None, number: int) -> str:
        err = self._require_number(number, "pr_checks")
        if err:
            return err
        return run_gh(["pr", "checks", str(number)], repo=repo)

    def _issue_list(
        self,
        repo: str | None,
        state: str,
        limit: int,
        search: str,
    ) -> str:
        args = [
            "issue",
            "list",
            "--limit",
            str(limit),
            "--json",
            "number,title,state,url,author,labels,updatedAt",
        ]
        st = state.strip().lower()
        if st in ("open", "closed", "all"):
            args.extend(["--state", st])
        if search.strip():
            args.extend(["--search", search.strip()])
        return run_gh(args, repo=repo)

    def _issue_view(self, repo: str | None, number: int) -> str:
        err = self._require_number(number, "issue_view")
        if err:
            return err
        return run_gh(
            [
                "issue",
                "view",
                str(number),
                "--json",
                "number,title,body,state,url,author,labels,assignees,comments",
            ],
            repo=repo,
        )

    def _run_list(self, repo: str | None, limit: int, branch: str) -> str:
        args = [
            "run",
            "list",
            "--limit",
            str(limit),
            "--json",
            "databaseId,displayTitle,status,conclusion,event,headBranch,url,createdAt,updatedAt",
        ]
        if branch.strip():
            args.extend(["--branch", branch.strip()])
        return run_gh(args, repo=repo)

    def _run_view(self, repo: str | None, number: int) -> str:
        err = self._require_number(number, "run_view")
        if err:
            return err
        return run_gh(
            [
                "run",
                "view",
                str(number),
                "--json",
                "databaseId,displayTitle,status,conclusion,event,headBranch,url,"
                "createdAt,updatedAt,jobs",
            ],
            repo=repo,
        )

    @staticmethod
    def _normalize_branch(name: str, label: str) -> str | None:
        cleaned = name.strip()
        if not cleaned:
            return f"ERROR: {label} is required."
        if not _BRANCH_PATTERN.match(cleaned):
            return f"ERROR: invalid {label} {name!r}."
        return cleaned

    def _branch_compare(
        self,
        repo: str | None,
        base_branch: str,
        head_branch: str,
    ) -> str:
        if not repo:
            return "ERROR: branch_compare requires repo (owner/name)."
        base = self._normalize_branch(base_branch, "base_branch")
        if base and base.startswith("ERROR"):
            return base
        head = self._normalize_branch(head_branch, "head_branch")
        if head and head.startswith("ERROR"):
            return head
        compare_ref = f"{base}...{head}"
        endpoint = f"/repos/{repo}/compare/{compare_ref}"
        jq_filter = (
            "{status,ahead_by,behind_by,total_commits,"
            "commits:[.commits[]|.commit|{message:.message,author:.author.name}],"
            "files:[.files[]|{filename,status,additions,deletions,changes}]}"
        )
        return run_gh(
            ["api", endpoint, "--method", "GET", "--jq", jq_filter],
            repo=None,
        )

    def _repo_view(self, repo: str | None) -> str:
        return run_gh(
            [
                "repo",
                "view",
                "--json",
                "name,nameWithOwner,description,url,defaultBranchRef,isPrivate,"
                "pushedAt,updatedAt,primaryLanguage",
            ],
            repo=repo,
            repo_style="positional",
        )

    def _api_get(self, repo: str | None, endpoint: str) -> str:
        path = endpoint.strip()
        if not path:
            return "ERROR: api_get requires endpoint (path starting with /)."
        if not path.startswith("/"):
            path = f"/{path}"
        if not _API_ENDPOINT_PATTERN.match(path):
            return (
                "ERROR: endpoint must be a GitHub REST path starting with / "
                "(letters, numbers, /, ., -, _, %, {, } only)."
            )
        return run_gh(["api", path, "--method", "GET"], repo=repo)
