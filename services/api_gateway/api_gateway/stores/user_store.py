"""
File-backed user store with hot-reload.

Users are stored in a JSON file. The store checks the file's mtime on
every access and reloads automatically when the file changes. This
allows:
  - Manual editing of the file (changes are picked up instantly)
  - Admin API writes (other worker processes see the update)
"""

import hmac
import json
import logging
import secrets
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from api_gateway.models.user import User

logger = logging.getLogger(__name__)


class UserStore:
    """Manages API users via a JSON file with hot-reload."""

    def __init__(self, file_path: str):
        self._file_path = Path(file_path)
        self._users: list[User] = []
        self._last_mtime: float = 0.0
        self._load()

    # ------------------------------------------------------------------
    #  File I/O
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Load users from the JSON file."""
        if not self._file_path.exists():
            logger.warning(
                f"Users file not found at {self._file_path}. "
                "Starting with empty user list."
            )
            self._users = []
            self._last_mtime = 0.0
            return

        try:
            mtime = self._file_path.stat().st_mtime
            if mtime == self._last_mtime and self._users:
                return  # Already up to date

            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._users = [User(**item) for item in data]
            self._last_mtime = mtime
            logger.info(
                f"Loaded {len(self._users)} user(s) from {self._file_path}"
            )
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in users file: {e}")
        except Exception as e:
            logger.error(f"Failed to load users file: {e}")

    def _save(self) -> None:
        """Persist current users to the JSON file."""
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        data = [user.model_dump(mode="json") for user in self._users]
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        self._last_mtime = self._file_path.stat().st_mtime

    def _maybe_reload(self) -> None:
        """Reload from disk if the file has been modified externally."""
        if not self._file_path.exists():
            return
        try:
            mtime = self._file_path.stat().st_mtime
            if mtime != self._last_mtime:
                logger.debug("Users file changed — reloading")
                self._load()
        except OSError:
            pass

    # ------------------------------------------------------------------
    #  Authentication
    # ------------------------------------------------------------------

    def authenticate(self, api_key: str) -> Optional[User]:
        """
        Authenticate an API key.

        Uses constant-time comparison per user to prevent timing attacks.
        Skips inactive and expired users.
        """
        self._maybe_reload()
        now = datetime.now(timezone.utc)

        for user in self._users:
            if not user.is_active:
                continue
            if user.expires_at and user.expires_at < now:
                continue

            if hmac.compare_digest(
                    api_key.encode("utf-8"),
                    user.api_key.encode("utf-8"),
            ):
                return user

        return None

    # ------------------------------------------------------------------
    #  CRUD operations (used by admin router)
    # ------------------------------------------------------------------

    def list_users(self) -> list[User]:
        """Return all users."""
        self._maybe_reload()
        return list(self._users)

    def get_user(self, user_id: str) -> Optional[User]:
        """Return a single user by ID."""
        self._maybe_reload()
        return next((u for u in self._users if u.id == user_id), None)

    def add_user(
            self,
            name: str,
            email: Optional[str] = None,
            expires_at: Optional[datetime] = None,
            metadata: Optional[dict] = None,
    ) -> User:
        """Create a new user with a cryptographically-secure API key."""
        self._maybe_reload()

        user = User(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            api_key=secrets.token_urlsafe(32),
            is_active=True,
            expires_at=expires_at,
            metadata=metadata or {},
        )
        self._users.append(user)
        self._save()
        logger.info(f"Created user '{name}' (id={user.id})")
        return user

    def remove_user(self, user_id: str) -> bool:
        """Remove a user permanently."""
        self._maybe_reload()
        before = len(self._users)
        self._users = [u for u in self._users if u.id != user_id]
        if len(self._users) < before:
            self._save()
            logger.info(f"Removed user id={user_id}")
            return True
        return False

    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user (key remains on file but is rejected)."""
        self._maybe_reload()
        for user in self._users:
            if user.id == user_id:
                user.is_active = False
                self._save()
                logger.info(f"Deactivated user id={user_id}")
                return True
        return False

    def regenerate_api_key(self, user_id: str) -> Optional[User]:
        """Issue a new API key for an existing user."""
        self._maybe_reload()
        for user in self._users:
            if user.id == user_id:
                user.api_key = secrets.token_urlsafe(32)
                self._save()
                logger.info(f"Regenerated API key for user id={user_id}")
                return user
        return None

    def bootstrap_user(
            self,
            *,
            api_key: str,
            name: str,
            email: Optional[str] = None,
    ) -> Optional[User]:
        """
        Create the initial API user from an environment-provided key.

        Bootstrap is intentionally conservative:
        - it only runs when the user store is empty;
        - it never overwrites existing users;
        - it never logs the API key;
        - it exists only to simplify first local startup.
        """
        self._maybe_reload()

        if not api_key:
            return None

        if self._users:
            logger.info("Skipping API user bootstrap; user store is not empty")
            return None

        user = User(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            api_key=api_key,
            is_active=True,
            expires_at=None,
            metadata={"created_by": "bootstrap"},
        )

        self._users.append(user)
        self._save()

        logger.info("Bootstrapped initial API user from environment")
        return user
