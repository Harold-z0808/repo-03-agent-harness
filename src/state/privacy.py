"""A deliberately small pre-ingestion guard for synthetic classroom examples."""

import re

CARD_PATTERN = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def privacy_check(text: str) -> tuple[bool, list[str]]:
    reasons = []
    if CARD_PATTERN.search(text):
        reasons.append("possible_payment_card")
    if EMAIL_PATTERN.search(text):
        reasons.append("email_address")
    return not reasons, reasons


def redact_for_display(text: str) -> str:
    return EMAIL_PATTERN.sub("[REDACTED_EMAIL]", CARD_PATTERN.sub("[REDACTED_CARD]", text))


async def guarded_run(runner, agent, text: str, **kwargs):
    """Call the model/session only after the local guard accepts the raw text."""
    allowed, reasons = privacy_check(text)
    if not allowed:
        raise ValueError("Blocked before model/session ingestion: " + ", ".join(reasons))
    return await runner(agent, text, **kwargs)
