"""Dapr client wrapper for state management and service invocation."""

import os
from typing import Any


def is_dapr_available() -> bool:
    """Check if Dapr sidecar is available via environment variables."""
    return bool(os.environ.get("DAPR_API_TOKEN")) or bool(os.environ.get("DAPR_GRPC_ENDPOINT"))


class DaprStateClient:
    """Dapr state store client for caching scoring results."""

    def __init__(self, state_store: str = "statestore") -> None:
        """Initialize Dapr state client.

        Args:
            state_store: Name of the Dapr state store component.
        """
        self._state_store = state_store
        self._client = None
        self._enabled = is_dapr_available()

    def _get_client(self):
        """Lazily get or create Dapr client."""
        if self._client is None and self._enabled:
            try:
                from dapr.clients import DaprClient

                self._client = DaprClient()
            except Exception:
                self._enabled = False
        return self._client

    def get_state(self, key: str) -> dict[str, Any] | None:
        """Get state by key from Dapr state store.

        Args:
            key: State key.

        Returns:
            State value or None if not found.
        """
        client = self._get_client()
        if client is None:
            return None
        try:
            import json

            result = client.state.get_state(
                state_store=self._state_store,
                key=key,
            )
            if result:
                return json.loads(result)
            return None
        except Exception:
            return None

    def set_state(self, key: str, value: dict[str, Any], ttl_seconds: int | None = None) -> bool:
        """Set state in Dapr state store.

        Args:
            key: State key.
            value: State value.
            ttl_seconds: Optional TTL in seconds.

        Returns:
            True if successful, False otherwise.
        """
        client = self._get_client()
        if client is None:
            return False
        try:
            import json

            client.state.save_state(
                state_store=self._state_store,
                states=[{"key": key, "value": json.dumps(value)}],
            )
            return True
        except Exception:
            return False

    def delete_state(self, key: str) -> bool:
        """Delete state by key from Dapr state store.

        Args:
            key: State key.

        Returns:
            True if successful, False otherwise.
        """
        client = self._get_client()
        if client is None:
            return False
        try:
            client.state.delete_state(
                state_store=self._state_store,
                key=key,
            )
            return True
        except Exception:
            return False


class DaprServiceInvoker:
    """Dapr service invocation client."""

    def __init__(self) -> None:
        """Initialize Dapr service invoker."""
        self._client = None
        self._enabled = is_dapr_available()

    def _get_client(self):
        """Lazily get or create Dapr client."""
        if self._client is None and self._enabled:
            try:
                from dapr.clients import DaprClient

                self._client = DaprClient()
            except Exception:
                self._enabled = False
        return self._client

    def invoke_service(
        self,
        app_id: str,
        method: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Invoke a method on another Dapr service.

        Args:
            app_id: Target application ID.
            method: Method name to invoke.
            payload: Optional payload to send.

        Returns:
            Response data or None on failure.
        """
        client = self._get_client()
        if client is None:
            return None
        try:
            import json

            response = client.invoke_method(
                app_id=app_id,
                method=method,
                data=json.dumps(payload) if payload else "{}",
                http_verb="POST",
            )
            if response:
                return json.loads(response)
            return None
        except Exception:
            return None


def get_state_key(commit: str, prefix: str = "score") -> str:
    """Generate a state key for caching.

    Args:
        commit: Git commit SHA.
        prefix: Key prefix.

    Returns:
        Generated state key.
    """
    return f"{prefix}:{commit}"
