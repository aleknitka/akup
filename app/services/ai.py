from __future__ import annotations

from abc import ABC, abstractmethod


class AIDescriptionService(ABC):
    @abstractmethod
    async def generate_description(
        self, commit_sha: str, repo_url: str, description: str
    ) -> str: ...


class PlaceholderAIService(AIDescriptionService):
    async def generate_description(self, commit_sha: str, repo_url: str, description: str) -> str:
        return (
            f"[AI placeholder] Evidence for commit {commit_sha[:8]} in {repo_url}: {description}"
        )


def get_ai_service() -> AIDescriptionService:
    return PlaceholderAIService()
