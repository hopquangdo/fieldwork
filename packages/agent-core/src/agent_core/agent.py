from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Sequence

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AnyMessage, BaseMessage, HumanMessage
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent

from .models import get_chat_model, model_from_env

UserContent = str | list[dict | str]


@dataclass
class Agent:
    """A thin, reusable wrapper around a LangGraph ReAct agent.

    `Agent.create(tools=..., model=..., system=...)` gives you a runnable that
    loops: model -> tool calls -> tool results -> model, until the model stops
    calling tools. Any LangChain `BaseTool` works; nothing here knows about a
    specific task.
    """

    model: BaseChatModel
    tools: list[BaseTool]
    system: str = ""
    graph: Any = field(default=None, repr=False)

    @classmethod
    def create(
        cls,
        tools: Iterable[BaseTool],
        *,
        model: str | BaseChatModel | None = None,
        system: str = "",
        checkpointer: Any | None = None,
        **model_kwargs: Any,
    ) -> "Agent":
        chat = model_from_env(**model_kwargs) if model is None else get_chat_model(model, **model_kwargs)
        tool_list = list(tools)
        graph = create_react_agent(
            chat,
            tool_list,
            prompt=system or None,
            checkpointer=checkpointer,
        )
        return cls(model=chat, tools=tool_list, system=system, graph=graph)

    def _input(self, user_content: UserContent, history: Sequence[AnyMessage] | None) -> dict:
        msgs: list[AnyMessage] = list(history or [])
        msgs.append(HumanMessage(content=user_content))
        return {"messages": msgs}

    def run(
        self,
        user_content: UserContent,
        *,
        history: Sequence[AnyMessage] | None = None,
        config: dict | None = None,
    ) -> list[BaseMessage]:
        out = self.graph.invoke(self._input(user_content, history), config=config)
        return out["messages"]

    def stream(
        self,
        user_content: UserContent,
        *,
        history: Sequence[AnyMessage] | None = None,
        config: dict | None = None,
    ):
        """Yield the message list after every graph step (stream_mode='values')."""
        yield from self.graph.stream(
            self._input(user_content, history), config=config, stream_mode="values"
        )
