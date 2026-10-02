"""Model theo ``.env`` (LLM_MODEL_NAME / LLM_API_KEY) + đếm token/chi phí cả lượt chạy."""
from __future__ import annotations

from infrastructure import llm as _llm
from infrastructure.llm import Usage, UsageTracker, model_name_of


class LLM:
    def __init__(self) -> None:
        self.usage = Usage()
        self._model = None

    @staticmethod
    def available() -> bool:
        return _llm.available()

    @property
    def model(self):
        if self._model is None:
            self._model = _llm.model()
            self.usage.model = model_name_of(self._model)
        return self._model

    @property
    def name(self) -> str:
        return self.usage.model or model_name_of(self.model)

    def structured(self, schema):
        return self.model.with_structured_output(schema)

    def config(self) -> dict:
        return {"callbacks": [UsageTracker(self.usage)]}
