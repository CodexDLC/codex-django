from dataclasses import dataclass


@dataclass
class AppointmentDisplayData:
    id: str
    title: str
    subtitle: str = ""
    status: str = ""
    status_tone: str = ""
    start_label: str = ""
    end_label: str = ""
    specialist_label: str = ""
    price_label: str = ""


__all__ = ["AppointmentDisplayData"]
