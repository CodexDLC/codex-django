from dataclasses import dataclass


@dataclass(frozen=True)
class InboxNotificationData:
    label: str
    count: int
    url: str
    icon: str = "bi-envelope"


__all__ = ["InboxNotificationData"]
