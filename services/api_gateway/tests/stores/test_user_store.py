import json
import time
from datetime import datetime, timedelta, timezone

from api_gateway.stores.user_store import UserStore


def test_add_and_authenticate_user(tmp_path):
    store = UserStore(str(tmp_path / "users.json"))
    user = store.add_user(name="Alice", email="alice@test.com")

    assert user.id is not None
    assert user.is_active is True
    assert len(user.api_key) > 20

    # Valid key
    auth_user = store.authenticate(user.api_key)
    assert auth_user.id == user.id

    # Invalid key
    assert store.authenticate("invalid-key") is None


def test_inactive_user_cannot_authenticate(tmp_path):
    store = UserStore(str(tmp_path / "users.json"))
    user = store.add_user(name="Bob")

    store.deactivate_user(user.id)
    assert store.authenticate(user.api_key) is None


def test_expired_user_cannot_authenticate(tmp_path):
    store = UserStore(str(tmp_path / "users.json"))
    past_date = datetime.now(timezone.utc) - timedelta(days=1)
    user = store.add_user(name="Charlie", expires_at=past_date)

    assert store.authenticate(user.api_key) is None


def test_remove_user(tmp_path):
    store = UserStore(str(tmp_path / "users.json"))
    user = store.add_user(name="Dave")

    assert store.remove_user(user.id) is True
    assert store.get_user(user.id) is None
    assert store.remove_user(user.id) is False


def test_regenerate_api_key(tmp_path):
    store = UserStore(str(tmp_path / "users.json"))
    user = store.add_user(name="Eve")
    old_key = user.api_key

    updated_user = store.regenerate_api_key(user.id)
    assert updated_user.api_key != old_key

    assert store.authenticate(old_key) is None
    assert store.authenticate(updated_user.api_key) is not None


def test_hot_reload_picks_up_external_changes(tmp_path):
    file_path = tmp_path / "users.json"
    store1 = UserStore(str(file_path))
    store1.add_user(name="Frank")

    # Create a second store instance pointing to the same file
    store2 = UserStore(str(file_path))
    assert len(store2.list_users()) == 1

    # Modify file externally
    time.sleep(0.1)  # Ensure mtime changes
    with open(str(file_path), "r") as f:
        data = json.load(f)
    data[0]["name"] = "Frank Updated"
    with open(str(file_path), "w") as f:
        json.dump(data, f)

    # store1 should pick up the change on next access
    users = store1.list_users()
    assert users[0].name == "Frank Updated"
