from __future__ import annotations

from collections.abc import Iterable

from groq import Groq

from ..config import Settings
from ..schemas import ChatMessage


class GroqClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = Groq(api_key=settings.groq_api_key)

    def transcribe_audio_file(self, audio_path: str) -> str:
        with open(audio_path, "rb") as audio_file:
            response = self._client.audio.transcriptions.create(
                model=self._settings.groq_whisper_model,
                file=audio_file,
            )
        return getattr(response, "text", str(response))

    def stream_answer(
        self,
        *,
        question: str,
        context_chunks: list[dict[str, str]],
        history: list[ChatMessage],
    ) -> Iterable[str]:
        messages = self._build_messages(question=question, context_chunks=context_chunks, history=history)
        stream = self._client.chat.completions.create(
            model=self._settings.groq_chat_model,
            messages=messages,
            stream=True,
            temperature=0.2,
        )
        for event in stream:
            delta = getattr(event.choices[0].delta, "content", None)
            if delta:
                yield delta

    def _build_messages(
        self,
        *,
        question: str,
        context_chunks: list[dict[str, str]],
        history: list[ChatMessage],
    ) -> list[dict[str, str]]:
        context_text = self._format_context(context_chunks)
        messages: list[dict[str, str]] = [
            {
                "role": "system",
                "content": (
                    "Tu es un assistant documentaire. Réponds uniquement à partir du contexte fourni. "
                    "Si le contexte ne suffit pas, dis-le clairement. Réponds dans la langue de l'utilisateur, "
                    "en français ou en anglais selon la question."
                ),
            }
        ]
        messages.extend({"role": item.role, "content": item.content} for item in history)
        messages.append(
            {
                "role": "user",
                "content": f"Contexte:\n{context_text or 'Aucun contexte pertinent trouvé.'}\n\nQuestion:\n{question}",
            }
        )
        return messages

    @staticmethod
    def _format_context(context_chunks: list[dict[str, str]]) -> str:
        parts: list[str] = []
        for index, chunk in enumerate(context_chunks, start=1):
            source = chunk.get("file_name", "source inconnue")
            text = chunk.get("text", "").strip()
            if text:
                parts.append(f"[{index}] {source}\n{text}")
        return "\n\n".join(parts)
