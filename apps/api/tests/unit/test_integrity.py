from clarion_api.services.integrity import compute_hash, verify
from tests.factories import approved_message


def test_hash_is_stable_and_prefixed() -> None:
    msg = approved_message()
    assert msg.integrity_hash is not None
    assert msg.integrity_hash.startswith("sha256:")
    assert compute_hash(msg) == msg.integrity_hash


def test_any_edit_breaks_verification() -> None:
    msg = approved_message()
    tampered = msg.model_copy(update={"summary": msg.summary + " "})
    assert verify(msg)
    assert not verify(tampered)


def test_chain_depends_on_previous_hash() -> None:
    msg = approved_message()
    assert compute_hash(msg, "sha256:aaa") != compute_hash(msg, "sha256:bbb")
