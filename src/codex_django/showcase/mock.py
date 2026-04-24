"""
Showcase Mock Data
==================
Temporary data for showcase UI development. Allows running all
showcase views without a database.

Replacement pattern (when real models are ready):
    # views.py — before:
    context = ShowcaseMockData.get_clients_context(segment=segment, q=q)
    # views.py — after:
    context = {"clients": Client.objects.all(), ...}  # ORM query
"""

from __future__ import annotations

from datetime import time
from typing import Any, cast

from codex_django.cabinet import (
    CalendarGridData,
    CalendarSlot,
    CardGridData,
    CardItem,
    ChartDatasetData,
    DataTableData,
    ListItem,
    ListRow,
    ListWidgetData,
    MetricWidgetData,
    ReportChartData,
    ReportPageData,
    ReportSummaryCardData,
    ReportTabData,
    ReportTableData,
    SidebarItem,
    SplitPanelData,
    TableColumn,
    TableFilter,
)


class ShowcaseMockData:
    """The sole source of mock data for all showcase views."""

    # ── Schedule constants ─────────────────────────────────────────────────────
    DAY_START: int = 8
    DAY_END: int = 20
    TOTAL_SLOTS: int = (DAY_END - DAY_START) * 2  # 24 slots × 30 min
    MIN_COL_PX: int = 160

    BOOKING_COLORS: list[str] = [
        "#6366f1",
        "#10b981",
        "#f59e0b",
        "#3b82f6",
        "#8b5cf6",
        "#f43f5e",
        "#14b8a6",
        "#f97316",
    ]

    # ── Staff ──────────────────────────────────────────────────────────────────
    STATUS_MAP: dict[str, dict[str, str]] = {
        "working": {"label": "Working", "bg": "#dcfce7", "color": "#16a34a"},
        "vacation": {"label": "On Vacation", "bg": "#fef9c3", "color": "#ca8a04"},
        "training": {"label": "In Training", "bg": "#dbeafe", "color": "#2563eb"},
        "fired": {"label": "Inactive", "bg": "#fee2e2", "color": "#dc2626"},
    }

    DAYS: list[str] = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]

    STAFF: list[dict[str, Any]] = [
        {
            "pk": 1,
            "name": "Lily",
            "role": "Founder & Top Stylist",
            "status": "working",
            "avatar": None,
            "initials": "L",
            "days": ["Mo", "Tu", "We", "Th", "Fr", "Sa"],
            "phone": "+49 176 5942 3704",
            "instagram": "@manikure_kothen",
            "experience": 10,
            "visible_on_site": True,
        },
        {
            "pk": 2,
            "name": "Nadezhda Miller",
            "role": "Beauty Master & Wellness Specialist",
            "status": "working",
            "avatar": None,
            "initials": "NM",
            "days": ["Mo", "Tu", "We", "Th", "Fr", "Sa"],
            "phone": "",
            "instagram": "",
            "experience": 2,
            "visible_on_site": True,
        },
        {
            "pk": 3,
            "name": "Liudmyla Andrukh",
            "role": "Top Nail Artist",
            "status": "working",
            "avatar": None,
            "initials": "LA",
            "days": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
            "phone": "",
            "instagram": "",
            "experience": 5,
            "visible_on_site": True,
        },
        {
            "pk": 4,
            "name": "Cosmetologist",
            "role": "Skincare Specialist",
            "status": "vacation",
            "avatar": None,
            "initials": "CS",
            "days": ["Mo", "Tu", "We", "Th", "Fr"],
            "phone": "",
            "instagram": "",
            "experience": 8,
            "visible_on_site": False,
        },
        {
            "pk": 5,
            "name": "Anna Smith",
            "role": "Administrator",
            "status": "training",
            "avatar": None,
            "initials": "AS",
            "days": ["Mo", "Tu", "We", "Th", "Fr"],
            "phone": "+49 170 1234 567",
            "instagram": "",
            "experience": 2,
            "visible_on_site": False,
        },
        {
            "pk": 6,
            "name": "Olga Peters",
            "role": "Nail Technician",
            "status": "fired",
            "avatar": None,
            "initials": "OP",
            "days": [],
            "phone": "",
            "instagram": "",
            "experience": 3,
            "visible_on_site": False,
        },
    ]

    STAFF_SEGMENTS: list[dict[str, Any]] = [
        {"key": "all", "label": "All", "icon": "bi-people", "fired": False},
        {"key": "working", "label": "Working", "icon": "bi-check-circle", "fired": False},
        {"key": "vacation", "label": "On Vacation", "icon": "bi-umbrella", "fired": False},
        {"key": "training", "label": "In Training", "icon": "bi-book", "fired": False},
        {"key": "fired", "label": "Inactive", "icon": "bi-slash-circle", "fired": True},
    ]

    # ── Booking ────────────────────────────────────────────────────────────────
    BOOKING_STAFF: list[dict[str, Any]] = [
        {"id": 1, "name": "Lily K.", "initials": "LK", "color": "#6366f1"},
        {"id": 2, "name": "Anna M.", "initials": "AM", "color": "#10b981"},
        {"id": 3, "name": "Kate R.", "initials": "KR", "color": "#f59e0b"},
    ]

    STATUS_META: dict[str, dict[str, str]] = {
        "confirmed": {"label": "Confirmed", "short": "Conf.", "color": "#22c55e", "bg": "#dcfce7"},
        "pending": {"label": "Pending", "short": "Pending", "color": "#d97706", "bg": "#fef3c7"},
        "cancelled": {"label": "Cancelled", "short": "Cancel", "color": "#ef4444", "bg": "#fee2e2"},
        "completed": {"label": "Completed", "short": "Done", "color": "#6366f1", "bg": "#e0e7ff"},
        "no_show": {"label": "No Show", "short": "No Show", "color": "#94a3b8", "bg": "#f1f5f9"},
    }

    APPOINTMENTS: list[dict[str, Any]] = [
        # Booking 1 — Johnson: manicure + pedicure (Lily)
        {
            "id": 1,
            "booking_id": 1,
            "staff_id": 1,
            "client": "Johnson A.",
            "phone": "+49 160 123 4567",
            "service": "Manicure + Gel Polish",
            "start": time(9, 0),
            "duration": 90,
            "status": "confirmed",
            "price": "$45",
        },
        {
            "id": 2,
            "booking_id": 1,
            "staff_id": 1,
            "client": "Johnson A.",
            "phone": "+49 160 123 4567",
            "service": "Basic Pedicure",
            "start": time(11, 0),
            "duration": 60,
            "status": "confirmed",
            "price": "$35",
        },
        # Booking 2 — Smith (Lily)
        {
            "id": 3,
            "booking_id": 2,
            "staff_id": 1,
            "client": "Smith N.",
            "phone": "+49 170 987 6543",
            "service": "Brow Design + Tinting",
            "start": time(12, 30),
            "duration": 45,
            "status": "pending",
            "price": "$25",
        },
        # Booking 3 — Berg (Lily)
        {
            "id": 4,
            "booking_id": 3,
            "staff_id": 1,
            "client": "Berg E.",
            "phone": "+49 177 888 9900",
            "service": "Lash Lamination",
            "start": time(15, 0),
            "duration": 60,
            "status": "confirmed",
            "price": "$55",
        },
        # Booking 4 — Miller (Anna)
        {
            "id": 5,
            "booking_id": 4,
            "staff_id": 2,
            "client": "Miller M.",
            "phone": "+49 151 555 1234",
            "service": "Haircut + Styling",
            "start": time(10, 0),
            "duration": 75,
            "status": "pending",
            "price": "$55",
        },
        # Booking 5 — Mueller (Anna)
        {
            "id": 6,
            "booking_id": 5,
            "staff_id": 2,
            "client": "Mueller A.",
            "phone": "+49 176 777 8899",
            "service": "Classic Manicure",
            "start": time(12, 0),
            "duration": 60,
            "status": "confirmed",
            "price": "$20",
        },
        # Booking 6 — Braun (Anna, hair coloring)
        {
            "id": 7,
            "booking_id": 6,
            "staff_id": 2,
            "client": "Braun K.",
            "phone": "+49 160 222 3344",
            "service": "Hair Coloring",
            "start": time(14, 0),
            "duration": 120,
            "status": "confirmed",
            "price": "$95",
        },
        # Booking 7 — Weber: massage (Kate)
        {
            "id": 8,
            "booking_id": 7,
            "staff_id": 3,
            "client": "Weber M.",
            "phone": "+49 152 333 4455",
            "service": "Back Massage",
            "start": time(9, 30),
            "duration": 60,
            "status": "confirmed",
            "price": "$35",
        },
        {
            "id": 9,
            "booking_id": 7,
            "staff_id": 3,
            "client": "Weber M.",
            "phone": "+49 152 333 4455",
            "service": "Leg Massage",
            "start": time(10, 30),
            "duration": 60,
            "status": "confirmed",
            "price": "$30",
        },
        # Booking 8 — Wilson (Kate)
        {
            "id": 10,
            "booking_id": 8,
            "staff_id": 3,
            "client": "Wilson K.",
            "phone": "+49 163 444 5566",
            "service": "Facial Treatment",
            "start": time(13, 0),
            "duration": 90,
            "status": "pending",
            "price": "$80",
        },
    ]

    SERVICES: list[dict[str, Any]] = [
        {
            "id": 1,
            "name": "Manicure + Gel Polish",
            "price": "$45",
            "price_raw": 45,
            "duration": 90,
            "category": "Nails",
        },
        {"id": 2, "name": "Basic Pedicure", "price": "$35", "price_raw": 35, "duration": 60, "category": "Nails"},
        {"id": 3, "name": "Pedicure + Polish", "price": "$50", "price_raw": 50, "duration": 75, "category": "Nails"},
        {
            "id": 4,
            "name": "Brow Design + Tinting",
            "price": "$25",
            "price_raw": 25,
            "duration": 45,
            "category": "Brows",
        },
        {"id": 5, "name": "Lash Lamination", "price": "$55", "price_raw": 55, "duration": 60, "category": "Brows"},
        {"id": 6, "name": "Haircut + Styling", "price": "$55", "price_raw": 55, "duration": 75, "category": "Hair"},
        {"id": 7, "name": "Hair Coloring", "price": "$95", "price_raw": 95, "duration": 120, "category": "Hair"},
        {"id": 8, "name": "Back Massage", "price": "$35", "price_raw": 35, "duration": 60, "category": "Massage"},
        {"id": 9, "name": "Leg Massage", "price": "$30", "price_raw": 30, "duration": 60, "category": "Massage"},
        {
            "id": 10,
            "name": "Facial Treatment",
            "price": "$80",
            "price_raw": 80,
            "duration": 90,
            "category": "Cosmetology",
        },
    ]

    CATEGORIES_BOOKING: list[dict[str, str]] = [
        {"name": "All"},
        {"name": "Nails"},
        {"name": "Brows"},
        {"name": "Hair"},
        {"name": "Massage"},
        {"name": "Cosmetology"},
    ]

    RECENT_CLIENTS: list[dict[str, Any]] = [
        {"name": "Anna Johnson", "initials": "AJ", "phone": "+49 160 123 4567", "visits": 12},
        {"name": "Maria Smith", "initials": "MS", "phone": "+49 151 555 1234", "visits": 5},
        {"name": "Nina Miller", "initials": "NM", "phone": "+49 170 987 6543", "visits": 3},
    ]

    CAL_DAYS_MARCH: list[dict[str, Any]] = [
        {"num": 23, "today": True, "current_month": True},
        {"num": 24, "today": False, "current_month": True},
        {"num": 25, "today": False, "current_month": True},
        {"num": 26, "today": False, "current_month": True},
        {"num": 27, "today": False, "current_month": True},
        {"num": 28, "today": False, "current_month": True},
        {"num": 29, "today": False, "current_month": True},
        {"num": 30, "today": False, "current_month": True},
        {"num": 31, "today": False, "current_month": True},
    ]

    TIME_OPTIONS: list[dict[str, Any]] = [
        {"time": "08:00", "busy": False},
        {"time": "08:30", "busy": False},
        {"time": "09:00", "busy": True},
        {"time": "09:30", "busy": True},
        {"time": "10:00", "busy": False},
        {"time": "10:30", "busy": True},
        {"time": "11:00", "busy": False},
        {"time": "11:30", "busy": False},
        {"time": "12:00", "busy": True},
        {"time": "12:30", "busy": True},
        {"time": "13:00", "busy": False},
        {"time": "13:30", "busy": False},
        {"time": "14:00", "busy": True},
        {"time": "14:30", "busy": False},
        {"time": "15:00", "busy": False},
        {"time": "15:30", "busy": False},
    ]

    STATUS_TABS: list[dict[str, str]] = [
        {"key": "all", "label": "All Appointments"},
        {"key": "pending", "label": "Pending"},
        {"key": "confirmed", "label": "Confirmed"},
        {"key": "completed", "label": "Completed"},
        {"key": "cancelled", "label": "Cancelled"},
    ]

    # ── Clients ────────────────────────────────────────────────────────────────
    CLIENT_STATUS_MAP: dict[str, dict[str, str]] = {
        "active": {"label": "Active", "bg": "#dcfce7", "color": "#16a34a"},
        "guest": {"label": "Guest", "bg": "#f1f5f9", "color": "#64748b"},
        "vip": {"label": "VIP", "bg": "#fef3c7", "color": "#d97706"},
        "new": {"label": "New", "bg": "#dbeafe", "color": "#2563eb"},
        "inactive": {"label": "Inactive", "bg": "#fee2e2", "color": "#dc2626"},
    }

    CLIENTS: list[dict[str, Any]] = [
        {
            "pk": 1,
            "name": "Cassandra Jahn",
            "status": "guest",
            "phone": "+49 176 4184 4825",
            "email": "cassandra-jahn@web.de",
            "last_visit": "22.03.2026",
        },
        {
            "pk": 2,
            "name": "Angelika Meyer",
            "status": "active",
            "phone": "+49 151 2331 8661",
            "email": "engel-meyer@gmx.de",
            "last_visit": "21.03.2026",
        },
        {
            "pk": 3,
            "name": "Mandy Drehkopf",
            "status": "vip",
            "phone": "+49 151 5202 9588",
            "email": "drehkopf87@web.de",
            "last_visit": "19.03.2026",
        },
        {
            "pk": 4,
            "name": "Antonia Oberman",
            "status": "active",
            "phone": "+49 176 3255 6681",
            "email": "a.oberman@gmx.net",
            "last_visit": "19.03.2026",
        },
        {
            "pk": 5,
            "name": "Grit Borns",
            "status": "guest",
            "phone": "+49 177 2754 449",
            "email": "g_borns@web.de",
            "last_visit": "19.03.2026",
        },
        {
            "pk": 6,
            "name": "Ellen Klos",
            "status": "new",
            "phone": "+49 176 5783 2126",
            "email": "u.klos@freenet.de",
            "last_visit": "18.03.2026",
        },
        {
            "pk": 7,
            "name": "Lena Mosert",
            "status": "active",
            "phone": "+49 179 5320 824",
            "email": "mosertlena@gmail.com",
            "last_visit": "17.03.2026",
        },
        {
            "pk": 8,
            "name": "Heike Westram",
            "status": "vip",
            "phone": "+49 151 5206 7249",
            "email": "kleineheike72@gmail.com",
            "last_visit": "16.03.2026",
        },
        {
            "pk": 9,
            "name": "Julia Smith",
            "status": "active",
            "phone": "",
            "email": "julia.smith@gmail.com",
            "last_visit": "13.03.2026",
        },
        {
            "pk": 10,
            "name": "Diana King",
            "status": "new",
            "phone": "+49 316 1556 1788",
            "email": "diana.king@gmail.com",
            "last_visit": "13.03.2026",
        },
        {
            "pk": 11,
            "name": "Jenny Lee",
            "status": "active",
            "phone": "+49 162 9266 520",
            "email": "jennylee@gmail.com",
            "last_visit": "13.03.2026",
        },
        {
            "pk": 12,
            "name": "Annett Hill",
            "status": "inactive",
            "phone": "",
            "email": "annett.hill@gmail.com",
            "last_visit": "11.03.2026",
        },
        {
            "pk": 13,
            "name": "Sophie Bahn",
            "status": "guest",
            "phone": "+49 151 5772 1762",
            "email": "sophie-bahn@gmx.de",
            "last_visit": "10.03.2026",
        },
        {
            "pk": 14,
            "name": "Agnes Lake",
            "status": "active",
            "phone": "+49 630 6035 650",
            "email": "agnes.lake@gmail.com",
            "last_visit": "10.03.2026",
        },
        {
            "pk": 15,
            "name": "Vivienne Bell",
            "status": "inactive",
            "phone": "+49 163 1316 997",
            "email": "",
            "last_visit": "06.03.2026",
        },
    ]

    CLIENT_SEGMENTS: list[dict[str, str]] = [
        {"key": "all", "label": "All Clients", "icon": "bi-people"},
        {"key": "active", "label": "Active", "icon": "bi-check-circle"},
        {"key": "guest", "label": "Guests", "icon": "bi-person-dash"},
        {"key": "vip", "label": "VIP", "icon": "bi-star"},
        {"key": "new", "label": "New", "icon": "bi-person-plus"},
        {"key": "inactive", "label": "Inactive", "icon": "bi-slash-circle"},
    ]

    # ── Conversations ──────────────────────────────────────────────────────────
    TOPICS: list[dict[str, Any]] = [
        {"pk": 1, "label": "General Inquiry"},
        {"pk": 2, "label": "Booking Questions"},
        {"pk": 3, "label": "Jobs / Careers"},
        {"pk": 4, "label": "Other"},
    ]

    CONVERSATIONS: list[dict[str, Any]] = [
        {
            "pk": 1,
            "topic": "Booking Questions",
            "client_name": "Elisa Berger",
            "client_email": "elli.bohme7@gmail.com",
            "client_phone": None,
            "client_whatsapp": "+49 176 1234 5678",
            "initials": "EB",
            "date": "15.03.2026",
            "status": "open",
            "preview": "Hello, I would like to book an appointment for a Hydrafacial treatment...",
            "initial_message": (
                "Hello dear team, I would like to book an appointment for a Hydrafacial treatment. "
                "I am getting married in June and would like to improve my skin before then, and "
                "hopefully continue coming to you afterwards if I am happy with the results.\n\n"
                "Is that possible, and if so, when? 🙂 Best regards, Elisa"
            ),
            "history": [
                {
                    "channel": "email",
                    "date": "15.03.2026 10:28",
                    "text": (
                        "Dear Elisa,\n\nThank you for your message via our website! First of all, "
                        "congratulations on your upcoming wedding.\n\nThe timing works perfectly: "
                        "if we start with the first Hydrafacial treatment next Saturday, the 21st "
                        "of March..."
                    ),
                },
            ],
        },
        {
            "pk": 2,
            "topic": "Booking Questions",
            "client_name": "Julia Smith",
            "client_email": "julia.smith@gmail.com",
            "client_phone": None,
            "client_whatsapp": None,
            "initials": "JS",
            "date": "13.03.2026",
            "status": "open",
            "preview": "Hello! Could you please let me know if you offer hair coloring services...",
            "initial_message": (
                "Hello! Could you please let me know if you offer hair coloring services and what the prices are?"
            ),
            "history": [],
        },
        {
            "pk": 3,
            "topic": "General Inquiry",
            "client_name": "Sophie Bahn",
            "client_email": "sophie-bahn@gmx.de",
            "client_phone": "+49 151 5772 1762",
            "client_whatsapp": "+49 151 5772 1762",
            "initials": "SB",
            "date": "10.03.2026",
            "status": "processed",
            "preview": "Good day, I would like to book an appointment for a facial treatment...",
            "initial_message": (
                "Good day, I would like to book an appointment for a facial treatment. "
                "Do you have any free slots this week?"
            ),
            "history": [
                {
                    "channel": "whatsapp",
                    "date": "10.03.2026 14:15",
                    "text": (
                        "Hello Sophie! Yes, we have slots available. Wednesday at 15:00 or "
                        "Thursday at 11:00. Which works better for you?"
                    ),
                },
                {
                    "channel": "whatsapp",
                    "date": "10.03.2026 14:42",
                    "text": "Wednesday at 15:00 would be perfect! See you then 😊",
                },
            ],
        },
        {
            "pk": 4,
            "topic": "Jobs / Careers",
            "client_name": "Anna Mueller",
            "client_email": "anna.mueller@web.de",
            "client_phone": None,
            "client_whatsapp": None,
            "initials": "AM",
            "date": "08.03.2026",
            "status": "processed",
            "preview": "Hello, I am a trained cosmetologist and interested in a position at your salon...",
            "initial_message": (
                "Hello, I am a trained cosmetologist with 3 years of experience and I am "
                "interested in a position at your salon. Are there any open positions at the moment?"
            ),
            "history": [
                {
                    "channel": "email",
                    "date": "09.03.2026 09:00",
                    "text": (
                        "Hello Anna, thank you for your application! Unfortunately we do not have "
                        "any open positions at the moment, but we would be happy to keep your "
                        "contact details on file..."
                    ),
                },
            ],
        },
    ]

    FOLDERS: list[dict[str, Any]] = [
        {"key": "inbox", "label": "Inbox", "icon": "bi-inbox", "statuses": ["open"]},
        {"key": "processed", "label": "Processed", "icon": "bi-check2-circle", "statuses": ["processed"]},
        {"key": "all", "label": "All", "icon": "bi-archive", "statuses": ["open", "processed"]},
    ]

    # ── Catalog ────────────────────────────────────────────────────────────────
    CATALOG_CATEGORIES: list[dict[str, Any]] = [
        {"pk": 1, "name": "Nail Services"},
        {"pk": 2, "name": "Brows & Lashes"},
        {"pk": 3, "name": "Hair Removal"},
    ]

    CATALOG_ITEMS: dict[int, list[dict[str, str]]] = {
        1: [
            {"label": "Classic Manicure", "value": "$20.00", "sublabel": "45 min"},
            {"label": "Manicure + Gel Polish", "value": "$45.00", "sublabel": "90 min"},
            {"label": "Nail Extension (gel)", "value": "$55.00", "sublabel": "120 min"},
            {"label": "Nail Extension (up to 3 cm)", "value": "$70.00", "sublabel": "150 min"},
        ],
        2: [
            {"label": "Brow Shaping + Tinting", "value": "$25.00", "sublabel": "45 min"},
            {"label": "Brow Lamination", "value": "$45.00", "sublabel": "50 min"},
            {"label": "Lash Extensions 2D–3D", "value": "$70.00", "sublabel": "120 min"},
            {"label": "Package: Lashes + Brows", "value": "$80.00", "sublabel": "50 min"},
        ],
        3: [
            {"label": "Upper Lip", "value": "$10.00", "sublabel": "15 min"},
            {"label": "Bikini Classic", "value": "$20.00", "sublabel": "30 min"},
            {"label": "Deep Bikini (Hollywood)", "value": "$35.00", "sublabel": "45 min"},
            {"label": "Package: Full Legs + Bikini", "value": "$50.00", "sublabel": "60 min"},
        ],
    }

    # ── Reports ────────────────────────────────────────────────────────────────
    REPORT_TABS: list[dict[str, str]] = [
        {"key": "revenue", "label": "Revenue", "icon": "bi-cash-stack"},
        {"key": "clients", "label": "Clients", "icon": "bi-people"},
        {"key": "staff", "label": "Staff", "icon": "bi-person-badge"},
        {"key": "services", "label": "Services", "icon": "bi-scissors"},
    ]

    PERIOD_OPTIONS: list[dict[str, str]] = [
        {"key": "week", "label": "Week"},
        {"key": "month", "label": "Month"},
        {"key": "quarter", "label": "Quarter"},
        {"key": "year", "label": "Year"},
    ]

    STAFF_OPTIONS: list[str] = ["All Staff", "Lily K.", "Anna M.", "Kate R."]

    REVENUE_COLUMNS: list[dict[str, Any]] = [
        {"key": "date", "label": "Date", "align": "left", "bold": True},
        {"key": "weekday", "label": "Day", "align": "left", "muted": True},
        {"key": "bookings_fmt", "label": "Bookings", "align": "right"},
        {"key": "revenue_fmt", "label": "Revenue", "align": "right", "bold": True},
        {"key": "avg_fmt", "label": "Avg. Check", "align": "right", "badge_key": "above_avg"},
        {"key": "top_master", "label": "Top Staff", "align": "left", "muted": True, "icon_key": "bi-person-fill"},
        {"key": "top_service", "label": "Top Service", "align": "left", "muted": True},
    ]

    _RAW_REVENUE: list[tuple[str, str, int, int, str, str, bool]] = [
        ("01.03", "Sun", 0, 0, "—", "—", True),
        ("02.03", "Mon", 4, 17500, "Lily K.", "Manicure + Gel Polish", False),
        ("03.03", "Tue", 6, 28200, "Anna M.", "Hair Coloring", False),
        ("04.03", "Wed", 5, 21000, "Lily K.", "Basic Pedicure", False),
        ("05.03", "Thu", 7, 35800, "Kate R.", "Facial Treatment", False),
        ("06.03", "Fri", 9, 42500, "Lily K.", "Manicure + Gel Polish", False),
        ("07.03", "Sat", 11, 54000, "Lily K.", "Manicure + Gel Polish", True),
        ("08.03", "Sun", 0, 0, "—", "—", True),
        ("09.03", "Mon", 5, 22300, "Anna M.", "Haircut + Styling", False),
        ("10.03", "Tue", 4, 18700, "Lily K.", "Brow Design + Tinting", False),
        ("11.03", "Wed", 6, 29400, "Kate R.", "Back Massage", False),
        ("12.03", "Thu", 8, 38100, "Lily K.", "Manicure + Gel Polish", False),
        ("13.03", "Fri", 10, 47600, "Anna M.", "Hair Coloring", False),
        ("14.03", "Sat", 12, 58200, "Lily K.", "Manicure + Gel Polish", True),
        ("15.03", "Sun", 0, 0, "—", "—", True),
        ("16.03", "Mon", 4, 19800, "Lily K.", "Basic Pedicure", False),
        ("17.03", "Tue", 5, 24500, "Kate R.", "Facial Treatment", False),
        ("18.03", "Wed", 6, 31000, "Lily K.", "Manicure + Gel Polish", False),
        ("19.03", "Thu", 7, 36700, "Anna M.", "Haircut + Styling", False),
        ("20.03", "Fri", 9, 44200, "Lily K.", "Manicure + Gel Polish", False),
        ("21.03", "Sat", 11, 53800, "Kate R.", "Facial Treatment", True),
        ("22.03", "Sun", 0, 0, "—", "—", True),
        ("23.03", "Mon", 5, 23400, "Lily K.", "Manicure + Gel Polish", False),
        ("24.03", "Tue", 4, 19100, "Anna M.", "Hair Coloring", False),
        ("25.03", "Wed", 6, 30500, "Lily K.", "Brow Design + Tinting", False),
        ("26.03", "Thu", 8, 39300, "Kate R.", "Facial Treatment", False),
        ("27.03", "Fri", 10, 49800, "Lily K.", "Manicure + Gel Polish", False),
        ("28.03", "Sat", 12, 61200, "Lily K.", "Manicure + Gel Polish", True),
        ("29.03", "Sun", 0, 0, "—", "—", True),
        ("30.03", "Mon", 4, 20100, "Anna M.", "Haircut + Styling", False),
        ("31.03", "Tue", 6, 28900, "Lily K.", "Basic Pedicure", False),
    ]

    # ── Private helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _to_slots(t: time) -> int:
        return ((t.hour - ShowcaseMockData.DAY_START) * 60 + t.minute) // 30

    @staticmethod
    def _dur_slots(minutes: int) -> int:
        return minutes // 30

    @staticmethod
    def _end_label(start: time, duration: int) -> str:
        total = start.hour * 60 + start.minute + duration
        return f"{total // 60:02d}:{total % 60:02d}"

    @staticmethod
    def _initials(name: str) -> str:
        parts = name.split()
        return "".join(p[0].upper() for p in parts[:2] if p)

    @staticmethod
    def _fmt_revenue(n: int) -> str:
        return f"${n:,}".replace(",", "\u202f") if n else "—"

    @staticmethod
    def _fmt_number(n: int) -> str:
        return str(n) if n else "—"

    @classmethod
    def _staff_map(cls) -> dict[int, dict[str, Any]]:
        return {s["id"]: s for s in cls.BOOKING_STAFF}

    @classmethod
    def _build_color_map(cls) -> dict[int, str]:
        color_map: dict[int, str] = {}
        idx = 0
        for appt in cls.APPOINTMENTS:
            bid = appt["booking_id"]
            if bid not in color_map:
                color_map[bid] = cls.BOOKING_COLORS[idx % len(cls.BOOKING_COLORS)]
                idx += 1
        return color_map

    @classmethod
    def _showcase_url(cls, name: str) -> str:
        urls = {
            "dashboard": "/showcase/dashboard/",
            "staff": "/showcase/staff/",
            "clients": "/showcase/clients/",
            "conversations": "/showcase/conversations/",
            "booking": "/showcase/booking/",
            "booking_appointments": "/showcase/booking/appointments/",
            "booking_new": "/showcase/booking/new/",
            "reports": "/showcase/analytics/reports/",
            "catalog": "/showcase/catalog/",
            "notifications_log": "/showcase/notifications/",
            "notifications_templates": "/showcase/notifications/templates/",
            "site_settings": "/showcase/site/settings/",
        }
        return urls[name]

    @classmethod
    def _shell_context(cls, active: str, *, label: str, icon: str = "bi-grid-3x3-gap-fill") -> dict[str, Any]:
        topbar_entries = [
            {"group": "admin", "label": "Dashboard", "icon": "bi-graph-up", "url": cls._showcase_url("dashboard")},
            {"group": "admin", "label": "Staff", "icon": "bi-person-badge", "url": cls._showcase_url("staff")},
            {"group": "admin", "label": "Clients", "icon": "bi-people", "url": cls._showcase_url("clients")},
            {"group": "admin", "label": "Reports", "icon": "bi-table", "url": cls._showcase_url("reports")},
            {"group": "services", "label": "Booking", "icon": "bi-calendar3", "url": cls._showcase_url("booking")},
            {"group": "services", "label": "Catalog", "icon": "bi-tag", "url": cls._showcase_url("catalog")},
            {
                "group": "services",
                "label": "Notifications",
                "icon": "bi-bell",
                "url": cls._showcase_url("notifications_log"),
            },
        ]
        return {
            "cabinet_branding": {"label": label, "icon": icon},
            "cabinet_active_topbar": {"label": label, "icon": icon},
            "cabinet_topbar_entries": topbar_entries,
            "cabinet_topbar_actions": [],
            "cabinet_quick_access": [],
            "cabinet_nav": [],
            "cabinet_sidebar": [],
            "cabinet_settings_url": cls._showcase_url("site_settings"),
            "cabinet_site_url": "/showcase/",
            "cabinet_logout_url": "",
            "cabinet_client_switch_url": "",
            "cabinet_staff_switch_url": "",
            "active_section": active,
        }

    @classmethod
    def _sidebar_item(
        cls,
        label: str,
        url: str,
        icon: str,
        *,
        active: bool = False,
        badge: int | str | None = None,
    ) -> SidebarItem:
        return SidebarItem(label=label, url=url, icon=icon, badge_key=str(badge) if badge else "")

    # ── Public classmethods ────────────────────────────────────────────────────

    @classmethod
    def get_dashboard_context(cls) -> dict[str, Any]:
        context = cls._shell_context("analytics", label="Analytics", icon="bi-graph-up")
        context.update(
            {
                "cabinet_sidebar": [
                    cls._sidebar_item("Dashboard", cls._showcase_url("dashboard"), "bi-grid", active=True),
                    cls._sidebar_item("Reports", cls._showcase_url("reports"), "bi-table"),
                ],
                "kpis": [
                    MetricWidgetData(
                        "Monthly Revenue",
                        "$115,500",
                        trend_value="+12%",
                        trend_label="vs last month",
                        trend_direction="up",
                        icon="bi-graph-up",
                    ),
                    MetricWidgetData(
                        "Monthly Appointments",
                        "47",
                        trend_value="+8%",
                        trend_label="vs last month",
                        trend_direction="up",
                        icon="bi-calendar-check",
                    ),
                    MetricWidgetData(
                        "Total Clients",
                        "30",
                        trend_value="+8",
                        trend_label="this week",
                        trend_direction="up",
                        icon="bi-people",
                    ),
                    MetricWidgetData(
                        "Average check",
                        "$2,457",
                        trend_value="+3%",
                        trend_label="vs last month",
                        trend_direction="up",
                        icon="bi-receipt",
                    ),
                ],
                "revenue_chart": {
                    "title": "Revenue",
                    "subtitle": "last 7 days",
                    "icon": "bi-bar-chart-line",
                    "type": "line",
                    "chart_labels": ["Mar 17", "Mar 18", "Mar 19", "Mar 20", "Mar 21", "Mar 22", "Today"],
                    "datasets": [
                        {
                            "data": [12400, 18200, 9800, 22100, 16500, 28400, 19200],
                            "borderColor": "#6366f1",
                            "backgroundColor": "rgba(99,102,241,0.08)",
                            "fill": True,
                            "tension": 0.4,
                        }
                    ],
                    "kpi_value": "$115,500",
                    "kpi_trend": "+12%",
                    "kpi_trend_label": "vs last month",
                    "height": "220px",
                },
                "services_donut": {
                    "title": "Services by categories",
                    "icon": "bi-pie-chart",
                    "chart_labels": ["Manicure", "Coloring", "Haircut", "Care"],
                    "chart_data": [45, 25, 20, 10],
                    "colors": ["#6366f1", "#10b981", "#f59e0b", "#3b82f6"],
                },
                "masters": ListWidgetData(
                    title="Top Specialists",
                    subtitle="this month",
                    icon="bi-trophy",
                    items=[
                        ListItem("Lily", "19 appointments", "L", subvalue="$89,500"),
                        ListItem("Jane Miller", "8 appointments", "JM", subvalue="$32,400"),
                        ListItem("Linda Adams", "6 appointments", "LA", subvalue="$24,800"),
                        ListItem("Cosmetologist", "2 appointments", "CS", subvalue="$8,600"),
                    ],
                ),
                "top_services": ListWidgetData(
                    title="Top Services",
                    subtitle="this month",
                    icon="bi-star",
                    items=[
                        ListItem("Manicure + Gel Polish Premium", "7 sales", subvalue="$31,500"),
                        ListItem("Package: Lashes + Brows", "4 sales", subvalue="$16,000"),
                        ListItem("Hair Coloring", "3 sales", subvalue="$13,500"),
                        ListItem("Smart Pedicure (Full)", "2 sales", subvalue="$11,000"),
                    ],
                ),
            }
        )
        return context

    @classmethod
    def get_staff_context(cls, *, segment: str = "all", q: str = "") -> dict[str, Any]:
        active_staff = [s for s in cls.STAFF if s["status"] != "fired"]
        fired_staff = [s for s in cls.STAFF if s["status"] == "fired"]

        pool: list[dict[str, Any]] = cls.STAFF if segment == "fired" else active_staff
        filtered: list[dict[str, Any]] = (
            pool if segment in ("all", "fired") else [s for s in pool if s["status"] == segment]
        )
        if q:
            filtered = [s for s in filtered if q in s["name"].lower() or q in s["role"].lower()]

        counts: dict[str, int] = {
            "all": len(active_staff),
            "working": sum(1 for s in active_staff if s["status"] == "working"),
            "vacation": sum(1 for s in active_staff if s["status"] == "vacation"),
            "training": sum(1 for s in active_staff if s["status"] == "training"),
            "fired": len(fired_staff),
        }
        segments_with_counts = [{**seg, "count": counts.get(seg["key"], 0)} for seg in cls.STAFF_SEGMENTS]

        cards = CardGridData(
            items=[
                CardItem(
                    id=str(person["pk"]),
                    title=person["name"],
                    subtitle=person["role"],
                    avatar=person["initials"],
                    badge=cls.STATUS_MAP.get(person["status"], {}).get("label", person["status"]),
                    badge_style="secondary",
                    url="#",
                    meta=[
                        ("bi-telephone", person["phone"] or "No phone"),
                        ("bi-briefcase", f"{person['experience']} years"),
                        (
                            "bi-eye" if person["visible_on_site"] else "bi-eye-slash",
                            "Visible" if person["visible_on_site"] else "Hidden",
                        ),
                    ],
                )
                for person in filtered
            ],
            search_placeholder="Search by name or specialization...",
            empty_message="Staff not found",
            avatar_size="36",
        )
        table = DataTableData(
            columns=[
                TableColumn("name", "Name", bold=True),
                TableColumn("role", "Role", muted=True),
                TableColumn("status_label", "Status", badge_key="status_colors"),
                TableColumn("days_label", "Days"),
                TableColumn("experience_label", "Experience"),
                TableColumn("site_label", "Site"),
            ],
            rows=[
                {
                    **person,
                    "status_label": cls.STATUS_MAP.get(person["status"], {}).get("label", person["status"]),
                    "status_colors": {
                        "working": "success",
                        "vacation": "warning",
                        "training": "info",
                        "fired": "secondary",
                    },
                    "days_label": ", ".join(person["days"]) or "—",
                    "experience_label": f"{person['experience']} years",
                    "site_label": "Visible" if person["visible_on_site"] else "Hidden",
                }
                for person in filtered
            ],
            empty_message="Staff not found",
        )
        context = cls._shell_context("staff", label="Staff", icon="bi-person-badge")
        context.update(
            {
                "cabinet_sidebar": [
                    cls._sidebar_item(
                        str(seg["label"]),
                        f"{cls._showcase_url('staff')}?segment={seg['key']}",
                        str(seg["icon"]),
                        active=segment == seg["key"],
                        badge=cast("int | str | None", seg["count"]),
                    )
                    for seg in segments_with_counts
                ],
                "staff": filtered,
                "segments": segments_with_counts,
                "active_segment": segment,
                "days_all": cls.DAYS,
                "status_map": cls.STATUS_MAP,
                "q": q,
                "total": len(filtered),
                "cards": cards,
                "table": table,
            }
        )
        return context

    @classmethod
    def get_clients_context(cls, *, segment: str = "all", q: str = "") -> dict[str, Any]:
        # Copy each dict to avoid mutating class-level CLIENTS on enrichment
        clients: list[dict[str, Any]] = [dict(c) for c in cls.CLIENTS]

        if segment != "all":
            clients = [c for c in clients if c.get("status") == segment]
        if q:
            clients = [
                c
                for c in clients
                if q in c.get("name", "").lower() or q in c.get("email", "").lower() or q in c.get("phone", "")
            ]

        for c in clients:
            c["status_meta"] = cls.CLIENT_STATUS_MAP.get(c.get("status"), cls.CLIENT_STATUS_MAP["guest"])  # type: ignore[arg-type]
            c["initials"] = "".join(p[0].upper() for p in c.get("name", "").split()[:2])

        counts: dict[str, int] = {"all": len(cls.CLIENTS)}
        for s in cls.CLIENT_SEGMENTS[1:]:
            key = s["key"]
            counts[key] = sum(1 for c in cls.CLIENTS if c.get("status") == key)
        segments_with_counts = [{**seg, "count": counts.get(seg["key"], 0)} for seg in cls.CLIENT_SEGMENTS]

        cards = CardGridData(
            items=[
                CardItem(
                    id=str(client["pk"]),
                    title=client["name"],
                    subtitle=client.get("email", ""),
                    avatar=client["initials"],
                    badge=client["status_meta"]["label"],
                    badge_style="secondary",
                    url="#",
                    meta=[
                        ("bi-telephone", client.get("phone") or "No phone"),
                        ("bi-envelope", client.get("email") or "No email"),
                        ("bi-calendar3", client.get("last_visit", "—")),
                    ],
                )
                for client in clients
            ],
            search_placeholder="Search by name, phone, email...",
            empty_message="No clients found",
        )
        table = DataTableData(
            columns=[
                TableColumn("name", "Name", bold=True),
                TableColumn("status_label", "Status", badge_key="status_colors"),
                TableColumn("phone", "Phone", muted=True),
                TableColumn("email", "Email", muted=True),
                TableColumn("last_visit", "Last Visit"),
            ],
            rows=[
                {
                    **client,
                    "status_label": client["status_meta"]["label"],
                    "status_colors": {"vip": "warning", "regular": "success", "new": "info", "guest": "secondary"},
                }
                for client in clients
            ],
            empty_message="No clients found",
        )
        context = cls._shell_context("clients", label="Clients", icon="bi-people")
        context.update(
            {
                "cabinet_sidebar": [
                    cls._sidebar_item(
                        str(seg["label"]),
                        f"{cls._showcase_url('clients')}?segment={seg['key']}",
                        str(seg["icon"]),
                        active=segment == seg["key"],
                        badge=cast("int | str | None", seg["count"]),
                    )
                    for seg in segments_with_counts
                ],
                "clients": clients,
                "segments": segments_with_counts,
                "active_segment": segment,
                "q": q,
                "total": len(clients),
                "cards": cards,
                "table": table,
            }
        )
        return context

    @classmethod
    def get_conversations_context(
        cls,
        *,
        folder: str = "inbox",
        topic_pk: str | None = None,
        q: str = "",
    ) -> dict[str, Any]:
        active_folder = next((f for f in cls.FOLDERS if f["key"] == folder), cls.FOLDERS[0])
        convs = [c for c in cls.CONVERSATIONS if c["status"] in active_folder["statuses"]]

        if topic_pk:
            topic_label = next((t["label"] for t in cls.TOPICS if str(t["pk"]) == topic_pk), None)
            if topic_label:
                convs = [c for c in convs if c["topic"] == topic_label]
        if q:
            convs = [c for c in convs if q in c["client_name"].lower() or q in c["preview"].lower()]

        counts: dict[str, int] = {
            "inbox": sum(1 for c in cls.CONVERSATIONS if c["status"] == "open"),
            "processed": sum(1 for c in cls.CONVERSATIONS if c["status"] == "processed"),
            "all": len(cls.CONVERSATIONS),
        }
        folders_with_counts = [{**f, "count": counts.get(f["key"])} for f in cls.FOLDERS]

        panel = SplitPanelData(
            items=[
                ListRow(
                    id=str(conv["pk"]),
                    primary=conv["client_name"],
                    secondary=conv["preview"],
                    meta=conv["date"],
                    avatar=conv["initials"],
                )
                for conv in convs
            ],
            detail_url=cls._showcase_url("conversations").rstrip("/"),
            empty_message="Select a conversation",
        )
        sidebar = [
            cls._sidebar_item(
                f["label"],
                f"{cls._showcase_url('conversations')}?folder={f['key']}",
                f["icon"],
                active=folder == f["key"],
                badge=f.get("count"),
            )
            for f in folders_with_counts
        ]
        sidebar.extend(
            [
                cls._sidebar_item(
                    "All Topics",
                    f"{cls._showcase_url('conversations')}?folder={folder}",
                    "bi-funnel",
                    active=not topic_pk,
                ),
                *[
                    cls._sidebar_item(
                        topic["label"],
                        f"{cls._showcase_url('conversations')}?folder={folder}&topic={topic['pk']}",
                        "bi-tag",
                        active=topic_pk == str(topic["pk"]),
                    )
                    for topic in cls.TOPICS
                ],
            ]
        )
        context = cls._shell_context("conversations", label="Conversations", icon="bi-chat-dots")
        context.update(
            {
                "cabinet_sidebar": sidebar,
                "conversations": convs,
                "folders": folders_with_counts,
                "topics": cls.TOPICS,
                "active_folder": folder,
                "active_topic": topic_pk,
                "q": q,
                "total": len(convs),
                "panel": panel,
            }
        )
        return context

    @classmethod
    def get_conversation_detail(cls, pk: int) -> dict[str, Any] | None:
        return next((c for c in cls.CONVERSATIONS if c["pk"] == pk), None)

    @classmethod
    def get_booking_schedule_context(cls) -> dict[str, Any]:
        time_slots: list[dict[str, Any]] = []
        for i, h in enumerate(range(cls.DAY_START, cls.DAY_END)):
            slot_idx = i * 2
            time_slots.append({"label": str(h), "sub": None, "is_hour": True, "slot_index": slot_idx})
            time_slots.append({"label": None, "sub": "30", "is_hour": False, "slot_index": slot_idx + 1})

        color_map = cls._build_color_map()
        appt_by_staff: dict[int, list[dict[str, Any]]] = {s["id"]: [] for s in cls.BOOKING_STAFF}

        for appt in cls.APPOINTMENTS:
            sm = cls.STATUS_META.get(str(appt.get("status")), cls.STATUS_META["confirmed"])
            start_time = appt.get("start")
            duration = appt.get("duration")
            staff_id = appt.get("staff_id")
            booking_id = appt.get("booking_id")
            client_name = appt.get("client", "")

            if (
                not isinstance(start_time, time)
                or not isinstance(duration, int)
                or not isinstance(staff_id, int)
                or not isinstance(booking_id, int)
            ):
                continue

            top_slots = cls._to_slots(start_time)
            dur_slots = cls._dur_slots(duration)
            appt_by_staff[staff_id].append(
                {
                    **appt,
                    "top_slots": top_slots,
                    "dur_slots": dur_slots,
                    "card_size": "full" if dur_slots >= 3 else ("mid" if dur_slots == 2 else "mini"),
                    "start_label": start_time.strftime("%H:%M"),
                    "end_label": cls._end_label(start_time, duration),
                    "booking_color": color_map.get(booking_id),
                    "status_label": sm["label"],
                    "status_short": sm["short"],
                    "status_color": sm["color"],
                    "status_bg": sm["bg"],
                    "initials": cls._initials(client_name),
                }
            )

        staff_list = [{**s, "appointments": appt_by_staff.get(s["id"], [])} for s in cls.BOOKING_STAFF]
        pending_count = sum(1 for a in cls.APPOINTMENTS if a.get("status") == "pending")

        rows = []
        events = []
        for h in range(cls.DAY_START, cls.DAY_END):
            rows.append({"hour": str(h), "min": "00"})
            rows.append({"hour": str(h), "min": "30"})
        for col_idx, staff in enumerate(staff_list):
            for appt in staff["appointments"]:
                color = appt.get("booking_color") or staff.get("color") or "#6366f1"
                events.append(
                    CalendarSlot(
                        col=col_idx,
                        row=appt["top_slots"],
                        span=appt["dur_slots"],
                        title=appt["client"],
                        subtitle=appt["service"],
                        color=f"{color}1c",
                        badge=appt["status_short"],
                        badge_style="dashed" if appt["status"] == "pending" else "",
                        price=appt["price"],
                        indicators=["bi-clock"],
                        url="#",
                        left_border=color,
                    )
                )
        calendar = CalendarGridData(
            cols=[
                {
                    "name": staff["name"],
                    "avatar": staff["initials"],
                    "color": staff["color"],
                    "info": f"{len(staff['appointments'])} appts.",
                }
                for staff in staff_list
            ],
            rows=rows,
            events=events,
            title="March 23, 2026",
            current_date="March 23, 2026",
            new_event_url=cls._showcase_url("booking_new"),
            slot_height="max(44px, calc((100vh - 165px) / 24))",
            time_col_width="44px",
            col_width=f"minmax({cls.MIN_COL_PX}px, 1fr)",
        )
        context = cls._shell_context("booking", label="Booking", icon="bi-calendar3")
        context.update(
            {
                "cabinet_sidebar": [
                    cls._sidebar_item("Schedule", cls._showcase_url("booking"), "bi-calendar3", active=True),
                    cls._sidebar_item(
                        "Appointments",
                        cls._showcase_url("booking_appointments"),
                        "bi-list-check",
                        badge=pending_count,
                    ),
                    cls._sidebar_item("New booking", cls._showcase_url("booking_new"), "bi-plus-circle"),
                ],
                "booking_tab": "schedule",
                "time_slots": time_slots,
                "total_slots": cls.TOTAL_SLOTS,
                "min_col_px": cls.MIN_COL_PX,
                "staff_list": staff_list,
                "current_date": "March 23, 2026",
                "pending_count": pending_count,
                "calendar": calendar,
            }
        )
        return context

    @classmethod
    def get_booking_appointments_context(cls, *, active_status: str = "all") -> dict[str, Any]:
        color_map = cls._build_color_map()
        staff_map = cls._staff_map()
        pending_count = sum(1 for a in cls.APPOINTMENTS if a.get("status") == "pending")

        pool = (
            cls.APPOINTMENTS
            if active_status == "all"
            else [a for a in cls.APPOINTMENTS if a.get("status") == active_status]
        )
        appointments: list[dict[str, Any]] = []
        for appt in pool:
            status = appt.get("status")
            staff_id = appt.get("staff_id")
            start_time = appt.get("start")
            duration = appt.get("duration")
            booking_id = appt.get("booking_id")
            client_name = appt.get("client", "")

            if not all([status, staff_id, start_time, isinstance(duration, int), booking_id]):
                continue

            sm = cls.STATUS_META.get(status, cls.STATUS_META["confirmed"])  # type: ignore[arg-type]
            staff = staff_map.get(staff_id, {})  # type: ignore[arg-type]
            appointments.append(
                {
                    **appt,
                    "start_label": start_time.strftime("%H:%M"),  # type: ignore[union-attr]
                    "end_label": cls._end_label(start_time, duration),  # type: ignore[arg-type]
                    "booking_color": color_map.get(booking_id),  # type: ignore[arg-type]
                    "initials": cls._initials(client_name),
                    "status_label": sm["label"],
                    "status_short": sm["short"],
                    "status_color": sm["color"],
                    "status_bg": sm["bg"],
                    "staff_name": staff.get("name", "—"),
                    "staff_initials": staff.get("initials", "—"),
                    "staff_color": staff.get("color", "#94a3b8"),
                }
            )

        counts: dict[str, int] = {}
        for tab in cls.STATUS_TABS:
            key = tab["key"]
            if key == "all":
                counts[key] = len(cls.APPOINTMENTS)
            else:
                counts[key] = sum(1 for a in cls.APPOINTMENTS if a.get("status") == key)
        status_tabs = [{**t, "count": counts[t["key"]]} for t in cls.STATUS_TABS]

        title_map: dict[str, str] = {
            "all": "All Appointments",
            "pending": "Pending Confirmation",
            "confirmed": "Confirmed",
            "completed": "Completed",
            "cancelled": "Cancelled",
        }
        table = DataTableData(
            columns=[
                TableColumn("client", "Client", bold=True),
                TableColumn("service", "Service"),
                TableColumn("staff_name", "Specialist"),
                TableColumn("date_time", "Date / Time"),
                TableColumn("price", "Price", align="right", bold=True),
                TableColumn("status_label", "Status", badge_key="status_colors"),
            ],
            rows=[
                {
                    **appt,
                    "date_time": f"23 March 2026 · {appt['start_label']} - {appt['end_label']}",
                    "status_colors": {
                        "confirmed": "success",
                        "pending": "warning",
                        "cancelled": "danger",
                        "completed": "primary",
                        "no_show": "secondary",
                    },
                }
                for appt in appointments
            ],
            filters=[
                TableFilter(
                    str(tab["key"]),
                    f"{tab['label']} ({tab['count']})",
                    "" if tab["key"] == "all" else str(tab["key"]),
                )
                for tab in status_tabs
            ],
            empty_message="No records found for the selected filters",
        )
        context = cls._shell_context("booking", label="Booking", icon="bi-calendar3")
        context.update(
            {
                "cabinet_sidebar": [
                    cls._sidebar_item("Schedule", cls._showcase_url("booking"), "bi-calendar3"),
                    cls._sidebar_item(
                        "Appointments",
                        cls._showcase_url("booking_appointments"),
                        "bi-list-check",
                        active=True,
                        badge=pending_count,
                    ),
                    cls._sidebar_item("New booking", cls._showcase_url("booking_new"), "bi-plus-circle"),
                ],
                "booking_tab": active_status if active_status != "all" else "all",
                "appointments": appointments,
                "status_tabs": status_tabs,
                "active_status": active_status,
                "page_title": title_map.get(active_status, "Appointments"),
                "pending_count": pending_count,
                "booking_new_url": cls._showcase_url("booking_new"),
                "table": table,
            }
        )
        return context

    @classmethod
    def get_booking_new_context(cls) -> dict[str, Any]:
        specialties = ["Nails, Brows", "Hair, Cosmetology", "Massage, Body Care"]
        staff_with_specialty = [{**s, "specialty": specialties[i]} for i, s in enumerate(cls.BOOKING_STAFF)]
        pending_count = sum(1 for a in cls.APPOINTMENTS if a.get("status") == "pending")
        context = cls._shell_context("booking", label="Booking", icon="bi-calendar3")
        context.update(
            {
                "cabinet_sidebar": [
                    cls._sidebar_item("Schedule", cls._showcase_url("booking"), "bi-calendar3"),
                    cls._sidebar_item(
                        "Appointments",
                        cls._showcase_url("booking_appointments"),
                        "bi-list-check",
                        badge=pending_count,
                    ),
                    cls._sidebar_item("New booking", cls._showcase_url("booking_new"), "bi-plus-circle", active=True),
                ],
                "booking_tab": "new",
                "services": cls.SERVICES,
                "categories": cls.CATEGORIES_BOOKING,
                "staff_list": staff_with_specialty,
                "recent_clients": cls.RECENT_CLIENTS,
                "cal_days": cls.CAL_DAYS_MARCH,
                "time_options": cls.TIME_OPTIONS,
                "pending_count": pending_count,
                "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            }
        )
        return context

    @classmethod
    def _build_revenue_rows(cls) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for date, wd, bk, rev, master, service, weekend in cls._RAW_REVENUE:
            avg = rev // bk if bk else 0
            rows.append(
                {
                    "date": date,
                    "weekday": wd,
                    "bookings": bk,
                    "revenue": rev,
                    "avg_check": avg,
                    "top_master": master,
                    "top_service": service,
                    "is_weekend": weekend,
                    "revenue_fmt": cls._fmt_revenue(rev),
                    "avg_fmt": cls._fmt_revenue(avg),
                    "bookings_fmt": cls._fmt_number(bk),
                }
            )
        return rows

    @classmethod
    def _revenue_summary(cls, rows: list[dict[str, Any]]) -> dict[str, Any]:
        total_b = sum(r["bookings"] for r in rows)
        total_r = sum(r["revenue"] for r in rows)
        avg_c = total_r // total_b if total_b else 0
        best = max(rows, key=lambda r: r["revenue"]) if rows else {}
        working = [r for r in rows if r["bookings"] > 0]
        return {
            "total_bookings": total_b,
            "total_revenue": cls._fmt_revenue(total_r),
            "avg_check": cls._fmt_revenue(avg_c),
            "best_day": best.get("date"),
            "best_day_val": cls._fmt_revenue(best.get("revenue", 0)),
            "working_days": len(working),
            "avg_check_raw": avg_c,
        }

    @classmethod
    def get_reports_context(cls, *, tab: str = "revenue", period: str = "month", staff: str = "") -> dict[str, Any]:
        rows = cls._build_revenue_rows()
        summary = cls._revenue_summary(rows)
        avg_raw = summary["avg_check_raw"]

        for r in rows:
            avg_check = r.get("avg_check", 0)
            r["above_avg"] = (avg_check >= avg_raw) if avg_check > 0 else None

        summary_row: dict[str, Any] = {
            "date": "Total · March 2026",
            "weekday": "",
            "bookings_fmt": str(summary["total_bookings"]),
            "revenue_fmt": summary["total_revenue"],
            "avg_fmt": summary["avg_check"],
            "top_master": "",
            "top_service": f"Working days: {summary['working_days']}",
        }
        report = ReportPageData(
            title="Reports",
            summary="Revenue, bookings, and operating metrics.",
            active_tab=tab,
            active_period=period,
            tabs=[ReportTabData(item["key"], item["label"], item.get("icon")) for item in cls.REPORT_TABS],
            period_options=[ReportTabData(item["key"], item["label"]) for item in cls.PERIOD_OPTIONS],
            period_label="March 2026",
            summary_cards=[
                ReportSummaryCardData("Revenue", summary["total_revenue"], hint="for March 2026", icon="bi-cash-stack"),
                ReportSummaryCardData(
                    "Bookings",
                    str(summary["total_bookings"]),
                    hint=f"working days: {summary['working_days']}",
                    icon="bi-calendar-check",
                ),
                ReportSummaryCardData("Average check", summary["avg_check"], hint="per booking", icon="bi-receipt"),
                ReportSummaryCardData("Best day", summary["best_day"], hint=summary["best_day_val"], icon="bi-trophy"),
            ],
            table=ReportTableData(
                columns=cls.REVENUE_COLUMNS,
                rows=rows,
                title="Revenue breakdown",
                subtitle="March 2026",
                summary_row=summary_row,
                primary_summary=summary["total_revenue"],
                secondary_summary=f"{summary['total_bookings']} bookings",
            ),
            chart=ReportChartData(
                chart_id="showcaseRevenueReport",
                title="Revenue trend",
                labels=[row["date"] for row in rows],
                datasets=[
                    ChartDatasetData(
                        "Revenue",
                        [row["revenue"] for row in rows],
                        border_color="#6366f1",
                        background_color="rgba(99,102,241,0.08)",
                        fill=True,
                        tension=0.35,
                    )
                ],
                description="Daily revenue",
                icon="bi-graph-up",
                height="260px",
                show_legend=False,
            ),
        )
        context = cls._shell_context("analytics", label="Analytics", icon="bi-graph-up")
        context.update(
            {
                "cabinet_sidebar": [
                    cls._sidebar_item("Dashboard", cls._showcase_url("dashboard"), "bi-grid"),
                    cls._sidebar_item("Reports", cls._showcase_url("reports"), "bi-table", active=True),
                ],
                "report_tabs": cls.REPORT_TABS,
                "period_options": cls.PERIOD_OPTIONS,
                "staff_options": cls.STAFF_OPTIONS,
                "active_tab": tab,
                "active_period": period,
                "active_staff": staff,
                "columns": cls.REVENUE_COLUMNS,
                "rows": rows,
                "summary_row": summary_row,
                "bar_max": 61200,
                "table_summary": summary,
                "period_label": "March 2026",
                "report": report,
            }
        )
        return context

    @classmethod
    def get_catalog_context(cls, *, category_pk: int | None = None) -> dict[str, Any]:
        active_category = next(
            (c for c in cls.CATALOG_CATEGORIES if c["pk"] == category_pk),
            cls.CATALOG_CATEGORIES[0],
        )
        list_widget = ListWidgetData(
            title=active_category["name"],
            icon="bi-tag",
            items=[
                ListItem(
                    label=item["label"],
                    value=item.get("value", ""),
                    sublabel=item.get("sublabel", ""),
                    subvalue=item.get("status", ""),
                )
                for item in cls.CATALOG_ITEMS.get(active_category["pk"], [])
            ],
        )
        context = cls._shell_context("catalog", label="Catalog", icon="bi-tag")
        context.update(
            {
                "cabinet_sidebar": [
                    cls._sidebar_item(
                        str(category["name"]),
                        f"{cls._showcase_url('catalog')}{category['pk']}/",
                        "bi-tag",
                        active=category["pk"] == active_category["pk"],
                    )
                    for category in cls.CATALOG_CATEGORIES
                ],
                "categories": cls.CATALOG_CATEGORIES,
                "active_category": active_category,
                "items": cls.CATALOG_ITEMS.get(active_category["pk"], []),
                "list_widget": list_widget,
            }
        )
        return context

    # ── Notifications ──────────────────────────────────────────────────────────

    _NOTIF_STATUSES: dict[str, dict[str, str]] = {
        "sent": {"label": "Sent", "color": "#16a34a", "bg": "#dcfce7"},
        "failed": {"label": "Failed", "color": "#dc2626", "bg": "#fee2e2"},
        "pending": {"label": "Pending", "color": "#d97706", "bg": "#fef3c7"},
    }

    _NOTIF_CHANNELS: dict[str, dict[str, str]] = {
        "email": {"label": "Email", "icon": "bi-envelope", "color": "#3b82f6", "bg": "#eff6ff"},
        "telegram": {"label": "Telegram", "icon": "bi-telegram", "color": "#0ea5e9", "bg": "#f0f9ff"},
    }

    _NOTIF_LOG_ENTRIES: list[dict[str, Any]] = [
        {
            "recipient": "Alice Johnson",
            "email": "alice@example.com",
            "channel": "email",
            "template_key": "booking_confirmed",
            "template_label": "Booking Confirmed",
            "subject": "Your booking is confirmed",
            "status": "sent",
            "sent_at": "26 Mar 2026, 14:32",
        },
        {
            "recipient": "Bob Martinez",
            "email": "bob@example.com",
            "channel": "telegram",
            "template_key": "booking_reminder",
            "template_label": "Booking Reminder",
            "subject": "Reminder: appointment tomorrow",
            "status": "sent",
            "sent_at": "26 Mar 2026, 12:00",
        },
        {
            "recipient": "Clara Müller",
            "email": "clara@example.com",
            "channel": "email",
            "template_key": "booking_cancelled",
            "template_label": "Booking Cancelled",
            "subject": "Your booking has been cancelled",
            "status": "sent",
            "sent_at": "26 Mar 2026, 10:15",
        },
        {
            "recipient": "David Lee",
            "email": "david@example.com",
            "channel": "email",
            "template_key": "welcome",
            "template_label": "Welcome",
            "subject": "Welcome to Codex Studio",
            "status": "failed",
            "sent_at": "25 Mar 2026, 18:44",
            "error": "SMTP connection timeout",
        },
        {
            "recipient": "Elena Kovač",
            "email": "elena@example.com",
            "channel": "telegram",
            "template_key": "booking_confirmed",
            "template_label": "Booking Confirmed",
            "subject": "Your booking is confirmed",
            "status": "sent",
            "sent_at": "25 Mar 2026, 16:20",
        },
        {
            "recipient": "Frank Nguyen",
            "email": "frank@example.com",
            "channel": "email",
            "template_key": "booking_reminder",
            "template_label": "Booking Reminder",
            "subject": "Reminder: appointment tomorrow",
            "status": "sent",
            "sent_at": "25 Mar 2026, 12:00",
        },
        {
            "recipient": "Grace Kim",
            "email": "grace@example.com",
            "channel": "email",
            "template_key": "password_reset",
            "template_label": "Password Reset",
            "subject": "Reset your password",
            "status": "sent",
            "sent_at": "25 Mar 2026, 09:31",
        },
        {
            "recipient": "Henry Popov",
            "email": "henry@example.com",
            "channel": "telegram",
            "template_key": "booking_cancelled",
            "template_label": "Booking Cancelled",
            "subject": "Your booking has been cancelled",
            "status": "failed",
            "sent_at": "24 Mar 2026, 20:05",
            "error": "Telegram API: bot blocked by user",
        },
        {
            "recipient": "Irina Sokolova",
            "email": "irina@example.com",
            "channel": "email",
            "template_key": "booking_confirmed",
            "template_label": "Booking Confirmed",
            "subject": "Your booking is confirmed",
            "status": "sent",
            "sent_at": "24 Mar 2026, 15:48",
        },
        {
            "recipient": "James Park",
            "email": "james@example.com",
            "channel": "email",
            "template_key": "welcome",
            "template_label": "Welcome",
            "subject": "Welcome to Codex Studio",
            "status": "sent",
            "sent_at": "24 Mar 2026, 11:22",
        },
        {
            "recipient": "Katrin Bauer",
            "email": "katrin@example.com",
            "channel": "telegram",
            "template_key": "booking_reminder",
            "template_label": "Booking Reminder",
            "subject": "Reminder: appointment tomorrow",
            "status": "pending",
            "sent_at": "27 Mar 2026, 08:00",
        },
        {
            "recipient": "Leon Dupont",
            "email": "leon@example.com",
            "channel": "email",
            "template_key": "booking_confirmed",
            "template_label": "Booking Confirmed",
            "subject": "Your booking is confirmed",
            "status": "sent",
            "sent_at": "23 Mar 2026, 17:10",
        },
        {
            "recipient": "Maya Okafor",
            "email": "maya@example.com",
            "channel": "email",
            "template_key": "booking_reminder",
            "template_label": "Booking Reminder",
            "subject": "Reminder: appointment tomorrow",
            "status": "sent",
            "sent_at": "23 Mar 2026, 12:00",
        },
        {
            "recipient": "Noah Fischer",
            "email": "noah@example.com",
            "channel": "telegram",
            "template_key": "booking_confirmed",
            "template_label": "Booking Confirmed",
            "subject": "Your booking is confirmed",
            "status": "sent",
            "sent_at": "23 Mar 2026, 09:45",
        },
        {
            "recipient": "Olivia Chen",
            "email": "olivia@example.com",
            "channel": "email",
            "template_key": "password_reset",
            "template_label": "Password Reset",
            "subject": "Reset your password",
            "status": "failed",
            "sent_at": "22 Mar 2026, 22:03",
            "error": "Mailbox full",
        },
        {
            "recipient": "Pavel Novak",
            "email": "pavel@example.com",
            "channel": "email",
            "template_key": "booking_cancelled",
            "template_label": "Booking Cancelled",
            "subject": "Your booking has been cancelled",
            "status": "sent",
            "sent_at": "22 Mar 2026, 14:27",
        },
        {
            "recipient": "Quinn Walsh",
            "email": "quinn@example.com",
            "channel": "telegram",
            "template_key": "welcome",
            "template_label": "Welcome",
            "subject": "Welcome to Codex Studio",
            "status": "sent",
            "sent_at": "22 Mar 2026, 10:58",
        },
        {
            "recipient": "Rosa García",
            "email": "rosa@example.com",
            "channel": "email",
            "template_key": "booking_confirmed",
            "template_label": "Booking Confirmed",
            "subject": "Your booking is confirmed",
            "status": "sent",
            "sent_at": "21 Mar 2026, 16:33",
        },
        {
            "recipient": "Sam Torres",
            "email": "sam@example.com",
            "channel": "email",
            "template_key": "booking_reminder",
            "template_label": "Booking Reminder",
            "subject": "Reminder: appointment tomorrow",
            "status": "pending",
            "sent_at": "27 Mar 2026, 08:00",
        },
        {
            "recipient": "Tanya Ivanova",
            "email": "tanya@example.com",
            "channel": "telegram",
            "template_key": "booking_confirmed",
            "template_label": "Booking Confirmed",
            "subject": "Your booking is confirmed",
            "status": "sent",
            "sent_at": "21 Mar 2026, 11:15",
        },
    ]

    _NOTIF_TEMPLATES: list[dict[str, Any]] = [
        {
            "key": "booking_confirmed",
            "label": "Booking Confirmed",
            "trigger": "On staff confirmation of booking",
            "channels": ["email", "telegram"],
            "subject": "Your booking is confirmed — {{ service_name }}",
            "preview": (
                "Hi {{ client_name }}, your appointment for {{ service_name }} "
                "with {{ staff_name }} is confirmed for {{ date }} at {{ time }}. "
                "We look forward to seeing you!"
            ),
        },
        {
            "key": "booking_cancelled",
            "label": "Booking Cancelled",
            "trigger": "On booking cancellation",
            "channels": ["email", "telegram"],
            "subject": "Your booking has been cancelled",
            "preview": (
                "Hi {{ client_name }}, unfortunately your appointment for "
                "{{ service_name }} on {{ date }} has been cancelled. "
                "Please contact us to reschedule."
            ),
        },
        {
            "key": "booking_reminder",
            "label": "Booking Reminder",
            "trigger": "24 hours before appointment (ARQ scheduled task)",
            "channels": ["email", "telegram"],
            "subject": "Reminder: your appointment is tomorrow",
            "preview": (
                "Hi {{ client_name }}, just a reminder that your appointment for "
                "{{ service_name }} with {{ staff_name }} is tomorrow at "
                "{{ time }}. See you soon!"
            ),
        },
        {
            "key": "welcome",
            "label": "Welcome",
            "trigger": "On new client registration",
            "channels": ["email"],
            "subject": "Welcome to {{ site_name }}",
            "preview": (
                "Welcome, {{ client_name }}! Your account has been created. "
                "You can now book appointments, track your visit history, and "
                "manage your settings in your personal cabinet."
            ),
        },
        {
            "key": "password_reset",
            "label": "Password Reset",
            "trigger": "On password reset request",
            "channels": ["email"],
            "subject": "Reset your password — {{ site_name }}",
            "preview": (
                "Hi {{ client_name }}, you requested a password reset. Click the "
                "link below to set a new password. The link is valid for 24 hours. "
                "If you did not request this, ignore this email."
            ),
        },
    ]

    @classmethod
    def get_notifications_log_context(cls, *, channel: str = "all", status: str = "all") -> dict[str, Any]:
        entries = []
        for entry in cls._NOTIF_LOG_ENTRIES:
            if channel != "all" and entry["channel"] != channel:
                continue
            if status != "all" and entry["status"] != status:
                continue
            ch = cls._NOTIF_CHANNELS[entry["channel"]]
            st = cls._NOTIF_STATUSES[entry["status"]]
            entries.append(
                {
                    **entry,
                    "channel_label": ch["label"],
                    "channel_icon": ch["icon"],
                    "channel_color": ch["color"],
                    "channel_bg": ch["bg"],
                    "status_label": st["label"],
                    "status_color": st["color"],
                    "status_bg": st["bg"],
                    "error": entry.get("error"),
                }
            )

        total = len(cls._NOTIF_LOG_ENTRIES)
        sent = sum(1 for e in cls._NOTIF_LOG_ENTRIES if e["status"] == "sent")
        failed = sum(1 for e in cls._NOTIF_LOG_ENTRIES if e["status"] == "failed")
        pending = sum(1 for e in cls._NOTIF_LOG_ENTRIES if e["status"] == "pending")
        status_tabs = [
            {"key": "all", "label": "All", "count": total},
            {"key": "sent", "label": "Sent", "count": sent},
            {"key": "failed", "label": "Failed", "count": failed},
            {"key": "pending", "label": "Pending", "count": pending},
        ]

        table = DataTableData(
            columns=[
                TableColumn("recipient", "Recipient", bold=True),
                TableColumn("channel_label", "Channel"),
                TableColumn("template_key", "Template"),
                TableColumn("created_at", "Created"),
                TableColumn("status_label", "Status", badge_key="status_colors"),
            ],
            rows=[
                {
                    **entry,
                    "status_colors": {"sent": "success", "failed": "danger", "pending": "warning"},
                }
                for entry in entries
            ],
            filters=[
                TableFilter(
                    str(tab["key"]),
                    f"{tab['label']} ({tab['count']})",
                    "" if tab["key"] == "all" else str(tab["key"]),
                )
                for tab in status_tabs
            ],
            empty_message="No notifications",
        )
        context = cls._shell_context("notifications", label="Notifications", icon="bi-bell")
        context.update(
            {
                "cabinet_sidebar": [
                    cls._sidebar_item(
                        "Log",
                        cls._showcase_url("notifications_log"),
                        "bi-bell",
                        active=True,
                        badge=cast("int | str | None", failed),
                    ),
                    cls._sidebar_item(
                        "Templates",
                        cls._showcase_url("notifications_templates"),
                        "bi-file-earmark-text",
                    ),
                ],
                "entries": entries,
                "active_channel": channel,
                "active_status": status,
                "stats": {"total": total, "sent": sent, "failed": failed, "pending": pending},
                "channel_tabs": [
                    {"key": "all", "label": "All channels", "count": total},
                    {
                        "key": "email",
                        "label": "Email",
                        "count": sum(1 for e in cls._NOTIF_LOG_ENTRIES if e["channel"] == "email"),
                    },
                    {
                        "key": "telegram",
                        "label": "Telegram",
                        "count": sum(1 for e in cls._NOTIF_LOG_ENTRIES if e["channel"] == "telegram"),
                    },
                ],
                "status_tabs": status_tabs,
                "table": table,
                "notification_total_kpi": MetricWidgetData("Total", str(total), icon="bi-bell"),
                "notification_sent_kpi": MetricWidgetData(
                    "Sent",
                    str(sent),
                    icon="bi-check-circle",
                    trend_direction="up",
                ),
                "notification_failed_kpi": MetricWidgetData(
                    "Failed",
                    str(failed),
                    icon="bi-exclamation-triangle",
                    trend_direction="down",
                ),
                "notification_pending_kpi": MetricWidgetData("Pending", str(pending), icon="bi-hourglass-split"),
            }
        )
        return context

    @classmethod
    def get_notification_templates_context(cls) -> dict[str, Any]:
        templates = []
        for tmpl in cls._NOTIF_TEMPLATES:
            channel_details = [cls._NOTIF_CHANNELS[ch] for ch in tmpl["channels"]]
            templates.append({**tmpl, "channel_details": channel_details})
        table = DataTableData(
            columns=[
                TableColumn("key", "Key", bold=True),
                TableColumn("label", "Label"),
                TableColumn("channels_label", "Channels"),
                TableColumn("subject", "Subject", muted=True),
            ],
            rows=[{**template, "channels_label": ", ".join(template["channels"])} for template in templates],
            empty_message="No templates",
        )
        context = cls._shell_context("notifications", label="Notifications", icon="bi-bell")
        context.update(
            {
                "cabinet_sidebar": [
                    cls._sidebar_item("Log", cls._showcase_url("notifications_log"), "bi-bell"),
                    cls._sidebar_item(
                        "Templates",
                        cls._showcase_url("notifications_templates"),
                        "bi-file-earmark-text",
                        active=True,
                    ),
                ],
                "templates": templates,
                "table": table,
            }
        )
        return context
