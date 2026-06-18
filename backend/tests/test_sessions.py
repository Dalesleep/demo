from app.sessions.store import get_session_store


def test_create_session():
    store = get_session_store()
    session = store.create()

    assert session.session_id
    assert session.active_skills == []


def test_reset_session():
    store = get_session_store()
    session = store.create()
    store.append_message(session.session_id, "user", "hello")

    assert store.reset(session.session_id) is True
    reset_session = store.get(session.session_id)
    assert reset_session is not None
    assert reset_session.messages == []


def test_active_skills_are_saved():
    store = get_session_store()
    session = store.create()

    assert store.set_active_skills(session.session_id, ["code-review", "test-generator"]) is True
    updated = store.get(session.session_id)
    assert updated is not None
    assert updated.active_skills == ["code-review", "test-generator"]

