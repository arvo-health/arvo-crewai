"""CrewAI LLM backend that delegates completions to Claude Code CLI (`claude -p`)."""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import TYPE_CHECKING, Any, Literal

from pydantic import Field

from crewai.events.types.llm_events import LLMCallType
from crewai.llms.base_llm import BaseLLM, llm_call_context

from arvo_auth.core.tools.notion_claude_delegate import run_claude_code_print

if TYPE_CHECKING:
    from pydantic import BaseModel

    from crewai.agents.agent_builder.base_agent import BaseAgent
    from crewai.task import Task
    from crewai.tools.base_tool import BaseTool
    from crewai.utilities.types import LLMMessage

logger = logging.getLogger(__name__)


def _content_to_str(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
            elif isinstance(block, str):
                parts.append(block)
            else:
                parts.append(json.dumps(block, ensure_ascii=False))
        return "\n".join(parts)
    if content is None:
        return ""
    return str(content)


def _messages_to_prompt(messages: list[Any]) -> str:
    chunks: list[str] = []
    for msg in messages:
        if not isinstance(msg, dict):
            chunks.append(str(msg))
            continue
        role = str(msg.get("role", "user"))
        body = _content_to_str(msg.get("content"))
        chunks.append(f"### {role.upper()}\n{body}")
    return "\n\n".join(chunks)


class ClaudeCodeLLM(BaseLLM):
    """Routes agent LLM calls through the local Claude Code binary (print mode, ReAct loop)."""

    llm_type: Literal["claude_code"] = "claude_code"
    model: str = Field(default="claude-code-cli")
    provider: str = Field(default="claude_code")
    is_litellm: bool = Field(default=False)

    def get_context_window_size(self) -> int:
        raw = os.getenv("ARVO_CLAUDE_CODE_CONTEXT_WINDOW", "").strip()
        if raw.isdigit():
            return int(raw)
        return 200_000

    def supports_stop_words(self) -> bool:
        """CLI transcript is one-shot; ReAct stop tokens must not trim subprocess output."""
        return False

    def call(
        self,
        messages: str | list[LLMMessage],
        tools: list[dict[str, BaseTool]] | None = None,
        callbacks: list[Any] | None = None,
        available_functions: dict[str, Any] | None = None,
        from_task: Task | None = None,
        from_agent: BaseAgent | None = None,
        response_model: type[BaseModel] | None = None,
    ) -> str | Any:
        with llm_call_context():
            self._emit_call_started_event(
                messages,
                tools,
                callbacks,
                available_functions,
                from_task,
                from_agent,
            )
            try:
                if isinstance(messages, str):
                    msgs: list[Any] = [{"role": "user", "content": messages}]
                else:
                    msgs = list(messages)

                if tools:
                    logger.warning(
                        "ClaudeCodeLLM received %d tool schema entries; native tool "
                        "calling is not supported. Use ReAct (default when this class has no "
                        "supports_function_calling).",
                        len(tools),
                    )

                prompt = _messages_to_prompt(msgs)
                if response_model is not None:
                    prompt += (
                        "\n\n### STRUCTURED_OUTPUT\nReply with a single JSON object only, "
                        "matching this schema:\n"
                        + json.dumps(response_model.model_json_schema(), indent=2)
                    )

                timeout_raw = (
                    os.getenv("ARVO_CREWAI_CLAUDE_CODE_TIMEOUT_SEC", "").strip()
                    or os.getenv("NOTION_CLAUDE_DELEGATE_TIMEOUT_SEC", "").strip()
                    or "3600"
                )
                timeout_sec = int(timeout_raw)
                text = run_claude_code_print(prompt, timeout_sec=timeout_sec)
                # Do not apply ReAct stop words (e.g. "\nObservation:") to a full CLI
                # transcript. CrewAI merges those into ``llm.stop`` for streaming APIs; on
                # ``claude -p`` they would truncate legitimate SRS text that echoes the
                # Thought/Action/Observation format or contains "Observation:" in prose.

                self._emit_call_completed_event(
                    response=text,
                    call_type=LLMCallType.LLM_CALL,
                    from_task=from_task,
                    from_agent=from_agent,
                    messages=messages,
                    usage=None,
                )
                return text
            except Exception as e:
                self._emit_call_failed_event(
                    str(e), from_task=from_task, from_agent=from_agent
                )
                raise

    async def acall(
        self,
        messages: str | list[LLMMessage],
        tools: list[dict[str, BaseTool]] | None = None,
        callbacks: list[Any] | None = None,
        available_functions: dict[str, Any] | None = None,
        from_task: Task | None = None,
        from_agent: BaseAgent | None = None,
        response_model: type[BaseModel] | None = None,
    ) -> str | Any:
        return await asyncio.to_thread(
            self.call,
            messages,
            tools,
            callbacks,
            available_functions,
            from_task,
            from_agent,
            response_model,
        )
