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
from typing import Any, Dict, List, Optional, Tuple


class ShowcaseMockData:
    """The sole source of mock data for all showcase views."""

    # ── Schedule constants ─────────────────────────────────────────────────────
    DAY_START: int = 8
    DAY_END: int = 20
    TOTAL_SLOTS: int = (DAY_END - DAY_START) * 2   # 24 slots × 30 min
    MIN_COL_PX: int = 160

    BOOKING_COLORS: List[str] = [
        "#6366f1", "#10b981", "#f59e0b", "#3b82f6",
        "#8b5cf6", "#f43f5e", "#14b8a6", "#f97316",
    ]

    # ── Staff ──────────────────────────────────────────────────────────────────
    STATUS_MAP: Dict[str, Dict[str, str]] = {
        "working":  {"label": "Working",     "bg": "#dcfce7", "color": "#16a34a"},
        "vacation": {"label": "On Vacation", "bg": "#fef9c3", "color": "#ca8a04"},
        "training": {"label": "In Training", "bg": "#dbeafe", "color": "#2563eb"},
        "fired":    {"label": "Inactive",    "bg": "#fee2e2", "color": "#dc2626"},
    }

    DAYS: List[str] = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]

    STAFF: List[Dict[str, Any]] = [
        {
            "pk": 1, "name": "Lily", "role": "Founder & Top Stylist",
            "status": "working", "avatar": None, "initials": "L",
            "days": ["Mo", "Tu", "We", "Th", "Fr", "Sa"],
            "phone": "+49 176 5942 3704", "instagram": "@manikure_kothen",
            "experience": 10, "visible_on_site": True,
        },
        {
            "pk": 2, "name": "Nadezhda Miller", "role": "Beauty Master & Wellness Specialist",
            "status": "working", "avatar": None, "initials": "NM",
            "days": ["Mo", "Tu", "We", "Th", "Fr", "Sa"],
            "phone": "", "instagram": "",
            "experience": 2, "visible_on_site": True,
        },
        {
            "pk": 3, "name": "Liudmyla Andrukh", "role": "Top Nail Artist",
            "status": "working", "avatar": None, "initials": "LA",
            "days": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
            "phone": "", "instagram": "",
            "experience": 5, "visible_on_site": True,
        },
        {
            "pk": 4, "name": "Cosmetologist", "role": "Skincare Specialist",
            "status": "vacation", "avatar": None, "initials": "CS",
            "days": ["Mo", "Tu", "We", "Th", "Fr"],
            "phone": "", "instagram": "",
            "experience": 8, "visible_on_site": False,
        },
        {
            "pk": 5, "name": "Anna Smith", "role": "Administrator",
            "status": "training", "avatar": None, "initials": "AS",
            "days": ["Mo", "Tu", "We", "Th", "Fr"],
            "phone": "+49 170 1234 567", "instagram": "",
            "experience": 2, "visible_on_site": False,
        },
        {
            "pk": 6, "name": "Olga Peters", "role": "Nail Technician",
            "status": "fired", "avatar": None, "initials": "OP",
            "days": [],
            "phone": "", "instagram": "",
            "experience": 3, "visible_on_site": False,
        },
    ]

    STAFF_SEGMENTS: List[Dict[str, Any]] = [
        {"key": "all",      "label": "All",         "icon": "bi-people",       "fired": False},
        {"key": "working",  "label": "Working",      "icon": "bi-check-circle", "fired": False},
        {"key": "vacation", "label": "On Vacation",  "icon": "bi-umbrella",     "fired": False},
        {"key": "training", "label": "In Training",  "icon": "bi-book",         "fired": False},
        {"key": "fired",    "label": "Inactive",     "icon": "bi-slash-circle", "fired": True},
    ]

    # ── Booking ────────────────────────────────────────────────────────────────
    BOOKING_STAFF: List[Dict[str, Any]] = [
        {"id": 1, "name": "Lily K.",   "initials": "LK", "color": "#6366f1"},
        {"id": 2, "name": "Anna M.",   "initials": "AM", "color": "#10b981"},
        {"id": 3, "name": "Kate R.",   "initials": "KR", "color": "#f59e0b"},
    ]

    STATUS_META: Dict[str, Dict[str, str]] = {
        "confirmed": {"label": "Confirmed",  "short": "Conf.",   "color": "#22c55e", "bg": "#dcfce7"},
        "pending":   {"label": "Pending",    "short": "Pending", "color": "#d97706", "bg": "#fef3c7"},
        "cancelled": {"label": "Cancelled",  "short": "Cancel",  "color": "#ef4444", "bg": "#fee2e2"},
        "completed": {"label": "Completed",  "short": "Done",    "color": "#6366f1", "bg": "#e0e7ff"},
        "no_show":   {"label": "No Show",    "short": "No Show", "color": "#94a3b8", "bg": "#f1f5f9"},
    }

    APPOINTMENTS: List[Dict[str, Any]] = [
        # Booking 1 — Johnson: manicure + pedicure (Lily)
        {"id": 1, "booking_id": 1, "staff_id": 1, "client": "Johnson A.", "phone": "+49 160 123 4567", "service": "Manicure + Gel Polish", "start": time(9, 0),   "duration": 90,  "status": "confirmed", "price": "$45"},
        {"id": 2, "booking_id": 1, "staff_id": 1, "client": "Johnson A.", "phone": "+49 160 123 4567", "service": "Basic Pedicure",        "start": time(11, 0),  "duration": 60,  "status": "confirmed", "price": "$35"},
        # Booking 2 — Smith (Lily)
        {"id": 3, "booking_id": 2, "staff_id": 1, "client": "Smith N.", "phone": "+49 170 987 6543", "service": "Brow Design + Tinting", "start": time(12, 30), "duration": 45,  "status": "pending",   "price": "$25"},
        # Booking 3 — Berg (Lily)
        {"id": 4, "booking_id": 3, "staff_id": 1, "client": "Berg E.",    "phone": "+49 177 888 9900", "service": "Lash Lamination",       "start": time(15, 0),  "duration": 60,  "status": "confirmed", "price": "$55"},
        # Booking 4 — Miller (Anna)
        {"id": 5, "booking_id": 4, "staff_id": 2, "client": "Miller M.", "phone": "+49 151 555 1234", "service": "Haircut + Styling",     "start": time(10, 0),  "duration": 75,  "status": "pending",   "price": "$55"},
        # Booking 5 — Mueller (Anna)
        {"id": 6, "booking_id": 5, "staff_id": 2, "client": "Mueller A.", "phone": "+49 176 777 8899", "service": "Classic Manicure",      "start": time(12, 0),  "duration": 60,  "status": "confirmed", "price": "$20"},
        # Booking 6 — Braun (Anna, hair coloring)
        {"id": 7, "booking_id": 6, "staff_id": 2, "client": "Braun K.",   "phone": "+49 160 222 3344", "service": "Hair Coloring",         "start": time(14, 0),  "duration": 120, "status": "confirmed", "price": "$95"},
        # Booking 7 — Weber: massage (Kate)
        {"id": 8, "booking_id": 7, "staff_id": 3, "client": "Weber M.",   "phone": "+49 152 333 4455", "service": "Back Massage",          "start": time(9, 30),  "duration": 60,  "status": "confirmed", "price": "$35"},
        {"id": 9, "booking_id": 7, "staff_id": 3, "client": "Weber M.",   "phone": "+49 152 333 4455", "service": "Leg Massage",           "start": time(10, 30), "duration": 60,  "status": "confirmed", "price": "$30"},
        # Booking 8 — Wilson (Kate)
        {"id": 10, "booking_id": 8, "staff_id": 3, "client": "Wilson K.", "phone": "+49 163 444 5566", "service": "Facial Treatment",    "start": time(13, 0),  "duration": 90,  "status": "pending",   "price": "$80"},
    ]

    SERVICES: List[Dict[str, Any]] = [
        {"id": 1,  "name": "Manicure + Gel Polish",   "price": "$45", "price_raw": 45, "duration": 90,  "category": "Nails"},
        {"id": 2,  "name": "Basic Pedicure",           "price": "$35", "price_raw": 35, "duration": 60,  "category": "Nails"},
        {"id": 3,  "name": "Pedicure + Polish",        "price": "$50", "price_raw": 50, "duration": 75,  "category": "Nails"},
        {"id": 4,  "name": "Brow Design + Tinting",   "price": "$25", "price_raw": 25, "duration": 45,  "category": "Brows"},
        {"id": 5,  "name": "Lash Lamination",          "price": "$55", "price_raw": 55, "duration": 60,  "category": "Brows"},
        {"id": 6,  "name": "Haircut + Styling",        "price": "$55", "price_raw": 55, "duration": 75,  "category": "Hair"},
        {"id": 7,  "name": "Hair Coloring",            "price": "$95", "price_raw": 95, "duration": 120, "category": "Hair"},
        {"id": 8,  "name": "Back Massage",             "price": "$35", "price_raw": 35, "duration": 60,  "category": "Massage"},
        {"id": 9,  "name": "Leg Massage",              "price": "$30", "price_raw": 30, "duration": 60,  "category": "Massage"},
        {"id": 10, "name": "Facial Treatment",         "price": "$80", "price_raw": 80, "duration": 90,  "category": "Cosmetology"},
    ]

    CATEGORIES_BOOKING: List[Dict[str, str]] = [
        {"name": "All"}, {"name": "Nails"}, {"name": "Brows"},
        {"name": "Hair"}, {"name": "Massage"}, {"name": "Cosmetology"},
    ]

    RECENT_CLIENTS: List[Dict[str, Any]] = [
        {"name": "Anna Johnson",  "initials": "AJ", "phone": "+49 160 123 4567", "visits": 12},
        {"name": "Maria Smith",   "initials": "MS", "phone": "+49 151 555 1234", "visits": 5},
        {"name": "Nina Miller",   "initials": "NM", "phone": "+49 170 987 6543", "visits": 3},
    ]

    CAL_DAYS_MARCH: List[Dict[str, Any]] = [
        {"num": 23, "today": True,  "current_month": True},
        {"num": 24, "today": False, "current_month": True},
        {"num": 25, "today": False, "current_month": True},
        {"num": 26, "today": False, "current_month": True},
        {"num": 27, "today": False, "current_month": True},
        {"num": 28, "today": False, "current_month": True},
        {"num": 29, "today": False, "current_month": True},
        {"num": 30, "today": False, "current_month": True},
        {"num": 31, "today": False, "current_month": True},
    ]

    TIME_OPTIONS: List[Dict[str, Any]] = [
        {"time": "08:00", "busy": False}, {"time": "08:30", "busy": False},
        {"time": "09:00", "busy": True},  {"time": "09:30", "busy": True},
        {"time": "10:00", "busy": False}, {"time": "10:30", "busy": True},
        {"time": "11:00", "busy": False}, {"time": "11:30", "busy": False},
        {"time": "12:00", "busy": True},  {"time": "12:30", "busy": True},
        {"time": "13:00", "busy": False}, {"time": "13:30", "busy": False},
        {"time": "14:00", "busy": True},  {"time": "14:30", "busy": False},
        {"time": "15:00", "busy": False}, {"time": "15:30", "busy": False},
    ]

    STATUS_TABS: List[Dict[str, str]] = [
        {"key": "all",       "label": "All Appointments"},
        {"key": "pending",   "label": "Pending"},
        {"key": "confirmed", "label": "Confirmed"},
        {"key": "completed", "label": "Completed"},
        {"key": "cancelled", "label": "Cancelled"},
    ]

    # ── Clients ────────────────────────────────────────────────────────────────
    CLIENT_STATUS_MAP: Dict[str, Dict[str, str]] = {
        "active":   {"label": "Active",   "bg": "#dcfce7", "color": "#16a34a"},
        "guest":    {"label": "Guest",    "bg": "#f1f5f9", "color": "#64748b"},
        "vip":      {"label": "VIP",      "bg": "#fef3c7", "color": "#d97706"},
        "new":      {"label": "New",      "bg": "#dbeafe", "color": "#2563eb"},
        "inactive": {"label": "Inactive", "bg": "#fee2e2", "color": "#dc2626"},
    }

    CLIENTS: List[Dict[str, Any]] = [
        {"pk": 1,  "name": "Cassandra Jahn",     "status": "guest",    "phone": "+49 176 4184 4825", "email": "cassandra-jahn@web.de",    "last_visit": "22.03.2026"},
        {"pk": 2,  "name": "Angelika Meyer",      "status": "active",   "phone": "+49 151 2331 8661", "email": "engel-meyer@gmx.de",       "last_visit": "21.03.2026"},
        {"pk": 3,  "name": "Mandy Drehkopf",      "status": "vip",      "phone": "+49 151 5202 9588", "email": "drehkopf87@web.de",        "last_visit": "19.03.2026"},
        {"pk": 4,  "name": "Antonia Oberman",     "status": "active",   "phone": "+49 176 3255 6681", "email": "a.oberman@gmx.net",        "last_visit": "19.03.2026"},
        {"pk": 5,  "name": "Grit Borns",          "status": "guest",    "phone": "+49 177 2754 449",  "email": "g_borns@web.de",           "last_visit": "19.03.2026"},
        {"pk": 6,  "name": "Ellen Klos",          "status": "new",      "phone": "+49 176 5783 2126", "email": "u.klos@freenet.de",        "last_visit": "18.03.2026"},
        {"pk": 7,  "name": "Lena Mosert",         "status": "active",   "phone": "+49 179 5320 824",  "email": "mosertlena@gmail.com",     "last_visit": "17.03.2026"},
        {"pk": 8,  "name": "Heike Westram",       "status": "vip",      "phone": "+49 151 5206 7249", "email": "kleineheike72@gmail.com",  "last_visit": "16.03.2026"},
        {"pk": 9,  "name": "Julia Smith",        "status": "active",   "phone": "",                  "email": "julia.smith@gmail.com",    "last_visit": "13.03.2026"},
        {"pk": 10, "name": "Diana King",         "status": "new",      "phone": "+49 316 1556 1788", "email": "diana.king@gmail.com",     "last_visit": "13.03.2026"},
        {"pk": 11, "name": "Jenny Lee",          "status": "active",   "phone": "+49 162 9266 520",  "email": "jennylee@gmail.com",       "last_visit": "13.03.2026"},
        {"pk": 12, "name": "Annett Hill",        "status": "inactive", "phone": "",                  "email": "annett.hill@gmail.com",    "last_visit": "11.03.2026"},
        {"pk": 13, "name": "Sophie Bahn",         "status": "guest",    "phone": "+49 151 5772 1762", "email": "sophie-bahn@gmx.de",       "last_visit": "10.03.2026"},
        {"pk": 14, "name": "Agnes Lake",         "status": "active",   "phone": "+49 630 6035 650",  "email": "agnes.lake@gmail.com",     "last_visit": "10.03.2026"},
        {"pk": 15, "name": "Vivienne Bell",      "status": "inactive", "phone": "+49 163 1316 997",  "email": "",                         "last_visit": "06.03.2026"},
    ]

    CLIENT_SEGMENTS: List[Dict[str, str]] = [
        {"key": "all",      "label": "All Clients", "icon": "bi-people"},
        {"key": "active",   "label": "Active",      "icon": "bi-check-circle"},
        {"key": "guest",    "label": "Guests",      "icon": "bi-person-dash"},
        {"key": "vip",      "label": "VIP",         "icon": "bi-star"},
        {"key": "new",      "label": "New",         "icon": "bi-person-plus"},
        {"key": "inactive", "label": "Inactive",    "icon": "bi-slash-circle"},
    ]

    # ── Conversations ──────────────────────────────────────────────────────────
    TOPICS: List[Dict[str, Any]] = [
        {"pk": 1, "label": "General Inquiry"},
        {"pk": 2, "label": "Booking Questions"},
        {"pk": 3, "label": "Jobs / Careers"},
        {"pk": 4, "label": "Other"},
    ]

    CONVERSATIONS: List[Dict[str, Any]] = [
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
            "initial_message": "Hello dear team, I would like to book an appointment for a Hydrafacial treatment. I am getting married in June and would like to improve my skin before then, and hopefully continue coming to you afterwards if I am happy with the results.\n\nIs that possible, and if so, when? 🙂 Best regards, Elisa",
            "history": [
                {"channel": "email", "date": "15.03.2026 10:28", "text": "Dear Elisa,\n\nThank you for your message via our website! First of all, congratulations on your upcoming wedding.\n\nThe timing works perfectly: if we start with the first Hydrafacial treatment next Saturday, the 21st of March..."},
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
            "initial_message": "Hello! Could you please let me know if you offer hair coloring services and what the prices are?",
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
            "initial_message": "Good day, I would like to book an appointment for a facial treatment. Do you have any free slots this week?",
            "history": [
                {"channel": "whatsapp", "date": "10.03.2026 14:15", "text": "Hello Sophie! Yes, we have slots available. Wednesday at 15:00 or Thursday at 11:00. Which works better for you?"},
                {"channel": "whatsapp", "date": "10.03.2026 14:42", "text": "Wednesday at 15:00 would be perfect! See you then 😊"},
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
            "initial_message": "Hello, I am a trained cosmetologist with 3 years of experience and I am interested in a position at your salon. Are there any open positions at the moment?",
            "history": [
                {"channel": "email", "date": "09.03.2026 09:00", "text": "Hello Anna, thank you for your application! Unfortunately we do not have any open positions at the moment, but we would be happy to keep your contact details on file..."},
            ],
        },
    ]

    FOLDERS: List[Dict[str, Any]] = [
        {"key": "inbox",     "label": "Inbox",     "icon": "bi-inbox",         "statuses": ["open"]},
        {"key": "processed", "label": "Processed", "icon": "bi-check2-circle", "statuses": ["processed"]},
        {"key": "all",       "label": "All",       "icon": "bi-archive",       "statuses": ["open", "processed"]},
    ]

    # ── Catalog ────────────────────────────────────────────────────────────────
    CATALOG_CATEGORIES: List[Dict[str, Any]] = [
        {"pk": 1, "name": "Nail Services"},
        {"pk": 2, "name": "Brows & Lashes"},
        {"pk": 3, "name": "Hair Removal"},
    ]

    CATALOG_ITEMS: Dict[int, List[Dict[str, str]]] = {
        1: [
            {"label": "Classic Manicure",            "value": "$20.00", "sublabel": "45 min"},
            {"label": "Manicure + Gel Polish",        "value": "$45.00", "sublabel": "90 min"},
            {"label": "Nail Extension (gel)",         "value": "$55.00", "sublabel": "120 min"},
            {"label": "Nail Extension (up to 3 cm)", "value": "$70.00", "sublabel": "150 min"},
        ],
        2: [
            {"label": "Brow Shaping + Tinting",  "value": "$25.00", "sublabel": "45 min"},
            {"label": "Brow Lamination",          "value": "$45.00", "sublabel": "50 min"},
            {"label": "Lash Extensions 2D–3D",   "value": "$70.00", "sublabel": "120 min"},
            {"label": "Package: Lashes + Brows", "value": "$80.00", "sublabel": "50 min"},
        ],
        3: [
            {"label": "Upper Lip",                      "value": "$10.00", "sublabel": "15 min"},
            {"label": "Bikini Classic",                 "value": "$20.00", "sublabel": "30 min"},
            {"label": "Deep Bikini (Hollywood)",        "value": "$35.00", "sublabel": "45 min"},
            {"label": "Package: Full Legs + Bikini",   "value": "$50.00", "sublabel": "60 min"},
        ],
    }

    # ── Reports ────────────────────────────────────────────────────────────────
    REPORT_TABS: List[Dict[str, str]] = [
        {"key": "revenue",  "label": "Revenue",  "icon": "bi-cash-stack"},
        {"key": "clients",  "label": "Clients",  "icon": "bi-people"},
        {"key": "staff",    "label": "Staff",    "icon": "bi-person-badge"},
        {"key": "services", "label": "Services", "icon": "bi-scissors"},
    ]

    PERIOD_OPTIONS: List[Dict[str, str]] = [
        {"key": "week",    "label": "Week"},
        {"key": "month",   "label": "Month"},
        {"key": "quarter", "label": "Quarter"},
        {"key": "year",    "label": "Year"},
    ]

    STAFF_OPTIONS: List[str] = ["All Staff", "Lily K.", "Anna M.", "Kate R."]

    REVENUE_COLUMNS: List[Dict[str, Any]] = [
        {"key": "date",         "label": "Date",       "align": "left",  "bold": True},
        {"key": "weekday",      "label": "Day",        "align": "left",  "muted": True},
        {"key": "bookings_fmt", "label": "Bookings",   "align": "right"},
        {"key": "revenue_fmt",  "label": "Revenue",    "align": "right", "bold": True},
        {"key": "avg_fmt",      "label": "Avg. Check", "align": "right", "badge_key": "above_avg"},
        {"key": "top_master",   "label": "Top Staff",  "align": "left",  "muted": True, "icon_key": "bi-person-fill"},
        {"key": "top_service",  "label": "Top Service","align": "left",  "muted": True},
    ]

    _RAW_REVENUE: List[Tuple[str, str, int, int, str, str, bool]] = [
        ("01.03", "Sun", 0,  0,      "—",        "—",                     True),
        ("02.03", "Mon", 4,  17500,  "Lily K.",  "Manicure + Gel Polish", False),
        ("03.03", "Tue", 6,  28200,  "Anna M.",  "Hair Coloring",         False),
        ("04.03", "Wed", 5,  21000,  "Lily K.",  "Basic Pedicure",        False),
        ("05.03", "Thu", 7,  35800,  "Kate R.",  "Facial Treatment",      False),
        ("06.03", "Fri", 9,  42500,  "Lily K.",  "Manicure + Gel Polish", False),
        ("07.03", "Sat", 11, 54000,  "Lily K.",  "Manicure + Gel Polish", True),
        ("08.03", "Sun", 0,  0,      "—",        "—",                     True),
        ("09.03", "Mon", 5,  22300,  "Anna M.",  "Haircut + Styling",     False),
        ("10.03", "Tue", 4,  18700,  "Lily K.",  "Brow Design + Tinting", False),
        ("11.03", "Wed", 6,  29400,  "Kate R.",  "Back Massage",          False),
        ("12.03", "Thu", 8,  38100,  "Lily K.",  "Manicure + Gel Polish", False),
        ("13.03", "Fri", 10, 47600,  "Anna M.",  "Hair Coloring",         False),
        ("14.03", "Sat", 12, 58200,  "Lily K.",  "Manicure + Gel Polish", True),
        ("15.03", "Sun", 0,  0,      "—",        "—",                     True),
        ("16.03", "Mon", 4,  19800,  "Lily K.",  "Basic Pedicure",        False),
        ("17.03", "Tue", 5,  24500,  "Kate R.",  "Facial Treatment",      False),
        ("18.03", "Wed", 6,  31000,  "Lily K.",  "Manicure + Gel Polish", False),
        ("19.03", "Thu", 7,  36700,  "Anna M.",  "Haircut + Styling",     False),
        ("20.03", "Fri", 9,  44200,  "Lily K.",  "Manicure + Gel Polish", False),
        ("21.03", "Sat", 11, 53800,  "Kate R.",  "Facial Treatment",      True),
        ("22.03", "Sun", 0,  0,      "—",        "—",                     True),
        ("23.03", "Mon", 5,  23400,  "Lily K.",  "Manicure + Gel Polish", False),
        ("24.03", "Tue", 4,  19100,  "Anna M.",  "Hair Coloring",         False),
        ("25.03", "Wed", 6,  30500,  "Lily K.",  "Brow Design + Tinting", False),
        ("26.03", "Thu", 8,  39300,  "Kate R.",  "Facial Treatment",      False),
        ("27.03", "Fri", 10, 49800,  "Lily K.",  "Manicure + Gel Polish", False),
        ("28.03", "Sat", 12, 61200,  "Lily K.",  "Manicure + Gel Polish", True),
        ("29.03", "Sun", 0,  0,      "—",        "—",                     True),
        ("30.03", "Mon", 4,  20100,  "Anna M.",  "Haircut + Styling",     False),
        ("31.03", "Tue", 6,  28900,  "Lily K.",  "Basic Pedicure",        False),
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
    def _staff_map(cls) -> Dict[int, Dict[str, Any]]:
        return {s["id"]: s for s in cls.BOOKING_STAFF}

    @classmethod
    def _build_color_map(cls) -> Dict[int, str]:
        color_map: Dict[int, str] = {}
        idx = 0
        for appt in cls.APPOINTMENTS:
            bid = appt["booking_id"]
            if bid not in color_map:
                color_map[bid] = cls.BOOKING_COLORS[idx % len(cls.BOOKING_COLORS)]
                idx += 1
        return color_map

    # ── Public classmethods ────────────────────────────────────────────────────

    @classmethod
    def get_dashboard_context(cls) -> Dict[str, Any]:
        return {
            "masters": [
                {"avatar": "L",  "label": "Lily",          "value": "19 appointments", "subvalue": "$89,500"},
                {"avatar": "JM", "label": "Jane Miller",   "value": "8 appointments",  "subvalue": "$32,400"},
                {"avatar": "LA", "label": "Linda Adams",   "value": "6 appointments",  "subvalue": "$24,800"},
                {"avatar": "CS", "label": "Cosmetologist", "value": "2 appointments",  "subvalue": "$8,600"},
            ],
            "top_services": [
                {"label": "Manicure + Gel Polish Premium", "value": "7 sales", "subvalue": "$31,500"},
                {"label": "Package: Lashes + Brows",       "value": "4 sales", "subvalue": "$16,000"},
                {"label": "Hair Coloring",                 "value": "3 sales", "subvalue": "$13,500"},
                {"label": "Smart Pedicure (Full)",         "value": "2 sales", "subvalue": "$11,000"},
            ],
        }

    @classmethod
    def get_staff_context(cls, *, segment: str = "all", q: str = "") -> Dict[str, Any]:
        active_staff = [s for s in cls.STAFF if s["status"] != "fired"]
        fired_staff  = [s for s in cls.STAFF if s["status"] == "fired"]

        pool: List[Dict[str, Any]] = cls.STAFF if segment == "fired" else active_staff
        filtered: List[Dict[str, Any]] = pool if segment in ("all", "fired") else [s for s in pool if s["status"] == segment]
        if q:
            filtered = [s for s in filtered if q in s["name"].lower() or q in s["role"].lower()]

        counts: Dict[str, int] = {
            "all":      len(active_staff),
            "working":  sum(1 for s in active_staff if s["status"] == "working"),
            "vacation": sum(1 for s in active_staff if s["status"] == "vacation"),
            "training": sum(1 for s in active_staff if s["status"] == "training"),
            "fired":    len(fired_staff),
        }
        segments_with_counts = [{**seg, "count": counts.get(seg["key"], 0)} for seg in cls.STAFF_SEGMENTS]

        return {
            "staff":          filtered,
            "segments":       segments_with_counts,
            "active_segment": segment,
            "days_all":       cls.DAYS,
            "status_map":     cls.STATUS_MAP,
            "q":              q,
            "total":          len(filtered),
        }

    @classmethod
    def get_clients_context(cls, *, segment: str = "all", q: str = "") -> Dict[str, Any]:
        # Copy each dict to avoid mutating class-level CLIENTS on enrichment
        clients: List[Dict[str, Any]] = [dict(c) for c in cls.CLIENTS]

        if segment != "all":
            clients = [c for c in clients if c.get("status") == segment]
        if q:
            clients = [
                c for c in clients
                if q in c.get("name", "").lower() or q in c.get("email", "").lower() or q in c.get("phone", "")
            ]

        for c in clients:
            c["status_meta"] = cls.CLIENT_STATUS_MAP.get(c.get("status"), cls.CLIENT_STATUS_MAP["guest"])  # type: ignore[arg-type]
            c["initials"] = "".join(p[0].upper() for p in c.get("name", "").split()[:2])

        counts: Dict[str, int] = {"all": len(cls.CLIENTS)}
        for s in cls.CLIENT_SEGMENTS[1:]:
            key = s["key"]
            counts[key] = sum(1 for c in cls.CLIENTS if c.get("status") == key)
        segments_with_counts = [{**seg, "count": counts.get(seg["key"], 0)} for seg in cls.CLIENT_SEGMENTS]

        return {
            "clients":        clients,
            "segments":       segments_with_counts,
            "active_segment": segment,
            "q":              q,
            "total":          len(clients),
        }

    @classmethod
    def get_conversations_context(
        cls,
        *,
        folder: str = "inbox",
        topic_pk: Optional[str] = None,
        q: str = "",
    ) -> Dict[str, Any]:
        active_folder = next((f for f in cls.FOLDERS if f["key"] == folder), cls.FOLDERS[0])
        convs = [c for c in cls.CONVERSATIONS if c["status"] in active_folder["statuses"]]

        if topic_pk:
            topic_label = next((t["label"] for t in cls.TOPICS if str(t["pk"]) == topic_pk), None)
            if topic_label:
                convs = [c for c in convs if c["topic"] == topic_label]
        if q:
            convs = [c for c in convs if q in c["client_name"].lower() or q in c["preview"].lower()]

        counts: Dict[str, int] = {
            "inbox":     sum(1 for c in cls.CONVERSATIONS if c["status"] == "open"),
            "processed": sum(1 for c in cls.CONVERSATIONS if c["status"] == "processed"),
            "all":       len(cls.CONVERSATIONS),
        }
        folders_with_counts = [{**f, "count": counts.get(f["key"])} for f in cls.FOLDERS]

        return {
            "conversations": convs,
            "folders":       folders_with_counts,
            "topics":        cls.TOPICS,
            "active_folder": folder,
            "active_topic":  topic_pk,
            "q":             q,
            "total":         len(convs),
        }

    @classmethod
    def get_conversation_detail(cls, pk: int) -> Optional[Dict[str, Any]]:
        return next((c for c in cls.CONVERSATIONS if c["pk"] == pk), None)

    @classmethod
    def get_booking_schedule_context(cls) -> Dict[str, Any]:
        time_slots: List[Dict[str, Any]] = []
        for i, h in enumerate(range(cls.DAY_START, cls.DAY_END)):
            slot_idx = i * 2
            time_slots.append({"label": str(h), "sub": None, "is_hour": True,  "slot_index": slot_idx})
            time_slots.append({"label": None,   "sub": "30", "is_hour": False, "slot_index": slot_idx + 1})

        color_map = cls._build_color_map()
        appt_by_staff: Dict[int, List[Dict[str, Any]]] = {s["id"]: [] for s in cls.BOOKING_STAFF}

        for appt in cls.APPOINTMENTS:
            sm = cls.STATUS_META.get(str(appt.get("status")), cls.STATUS_META["confirmed"])
            start_time = appt.get("start")
            duration = appt.get("duration")
            staff_id = appt.get("staff_id")
            booking_id = appt.get("booking_id")
            client_name = appt.get("client", "")

            if not all([start_time, isinstance(duration, int), staff_id, booking_id]):
                continue

            top_slots = cls._to_slots(start_time)  # type: ignore[arg-type]
            dur_slots = cls._dur_slots(duration)  # type: ignore[arg-type]
            appt_by_staff[staff_id].append({  # type: ignore[index]
                **appt,
                "top_slots":     top_slots,
                "dur_slots":     dur_slots,
                "card_size":     "full" if dur_slots >= 3 else ("mid" if dur_slots == 2 else "mini"),
                "start_label":   start_time.strftime("%H:%M"),  # type: ignore[union-attr]
                "end_label":     cls._end_label(start_time, duration),  # type: ignore[arg-type]
                "booking_color": color_map.get(booking_id),  # type: ignore[arg-type]
                "status_label":  sm["label"],
                "status_short":  sm["short"],
                "status_color":  sm["color"],
                "status_bg":     sm["bg"],
                "initials":      cls._initials(client_name),
            })

        staff_list = [{**s, "appointments": appt_by_staff.get(s["id"], [])} for s in cls.BOOKING_STAFF]
        pending_count = sum(1 for a in cls.APPOINTMENTS if a.get("status") == "pending")

        return {
            "active_section": "booking",
            "booking_tab":    "schedule",
            "time_slots":     time_slots,
            "total_slots":    cls.TOTAL_SLOTS,
            "min_col_px":     cls.MIN_COL_PX,
            "staff_list":     staff_list,
            "current_date":   "March 23, 2026",
            "pending_count":  pending_count,
        }

    @classmethod
    def get_booking_appointments_context(cls, *, active_status: str = "all") -> Dict[str, Any]:
        color_map = cls._build_color_map()
        staff_map = cls._staff_map()
        pending_count = sum(1 for a in cls.APPOINTMENTS if a.get("status") == "pending")

        pool = cls.APPOINTMENTS if active_status == "all" else [
            a for a in cls.APPOINTMENTS if a.get("status") == active_status
        ]
        appointments: List[Dict[str, Any]] = []
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
            appointments.append({
                **appt,
                "start_label":    start_time.strftime("%H:%M"),  # type: ignore[union-attr]
                "end_label":      cls._end_label(start_time, duration),  # type: ignore[arg-type]
                "booking_color":  color_map.get(booking_id),  # type: ignore[arg-type]
                "initials":       cls._initials(client_name),
                "status_label":   sm["label"],
                "status_short":   sm["short"],
                "status_color":   sm["color"],
                "status_bg":      sm["bg"],
                "staff_name":     staff.get("name", "—"),
                "staff_initials": staff.get("initials", "—"),
                "staff_color":    staff.get("color", "#94a3b8"),
            })

        counts: Dict[str, int] = {}
        for tab in cls.STATUS_TABS:
            key = tab["key"]
            if key == "all":
                counts[key] = len(cls.APPOINTMENTS)
            else:
                counts[key] = sum(1 for a in cls.APPOINTMENTS if a.get("status") == key)
        status_tabs = [{**t, "count": counts[t["key"]]} for t in cls.STATUS_TABS]

        title_map: Dict[str, str] = {
            "all":       "All Appointments",
            "pending":   "Pending Confirmation",
            "confirmed": "Confirmed",
            "completed": "Completed",
            "cancelled": "Cancelled",
        }
        return {
            "active_section": "booking",
            "booking_tab":    active_status if active_status != "all" else "all",
            "appointments":   appointments,
            "status_tabs":    status_tabs,
            "active_status":  active_status,
            "page_title":     title_map.get(active_status, "Appointments"),
            "pending_count":  pending_count,
        }

    @classmethod
    def get_booking_new_context(cls) -> Dict[str, Any]:
        specialties = ["Nails, Brows", "Hair, Cosmetology", "Massage, Body Care"]
        staff_with_specialty = [
            {**s, "specialty": specialties[i]}
            for i, s in enumerate(cls.BOOKING_STAFF)
        ]
        pending_count = sum(1 for a in cls.APPOINTMENTS if a.get("status") == "pending")
        return {
            "active_section": "booking",
            "booking_tab":    "new",
            "services":       cls.SERVICES,
            "categories":     cls.CATEGORIES_BOOKING,
            "staff_list":     staff_with_specialty,
            "recent_clients": cls.RECENT_CLIENTS,
            "cal_days":       cls.CAL_DAYS_MARCH,
            "time_options":   cls.TIME_OPTIONS,
            "pending_count":  pending_count,
            "weekdays":       ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        }

    @classmethod
    def _build_revenue_rows(cls) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for date, wd, bk, rev, master, service, weekend in cls._RAW_REVENUE:
            avg = rev // bk if bk else 0
            rows.append({
                "date": date, "weekday": wd, "bookings": bk, "revenue": rev,
                "avg_check": avg, "top_master": master, "top_service": service,
                "is_weekend": weekend,
                "revenue_fmt":  cls._fmt_revenue(rev),
                "avg_fmt":      cls._fmt_revenue(avg),
                "bookings_fmt": cls._fmt_number(bk),
            })
        return rows

    @classmethod
    def _revenue_summary(cls, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_b = sum(r["bookings"] for r in rows)
        total_r = sum(r["revenue"]  for r in rows)
        avg_c   = total_r // total_b if total_b else 0
        best    = max(rows, key=lambda r: r["revenue"]) if rows else {}
        working = [r for r in rows if r["bookings"] > 0]
        return {
            "total_bookings": total_b,
            "total_revenue":  cls._fmt_revenue(total_r),
            "avg_check":      cls._fmt_revenue(avg_c),
            "best_day":       best.get("date"),
            "best_day_val":   cls._fmt_revenue(best.get("revenue", 0)),
            "working_days":   len(working),
            "avg_check_raw":  avg_c,
        }

    @classmethod
    def get_reports_context(
        cls, *, tab: str = "revenue", period: str = "month", staff: str = ""
    ) -> Dict[str, Any]:
        rows    = cls._build_revenue_rows()
        summary = cls._revenue_summary(rows)
        avg_raw = summary["avg_check_raw"]

        for r in rows:
            avg_check = r.get("avg_check", 0)
            r["above_avg"] = (avg_check >= avg_raw) if avg_check > 0 else None

        summary_row: Dict[str, Any] = {
            "date":         "Total · March 2026",
            "weekday":      "",
            "bookings_fmt": str(summary["total_bookings"]),
            "revenue_fmt":  summary["total_revenue"],
            "avg_fmt":      summary["avg_check"],
            "top_master":   "",
            "top_service":  f"Working days: {summary['working_days']}",
        }
        return {
            "active_section": "analytics",
            "report_tabs":    cls.REPORT_TABS,
            "period_options": cls.PERIOD_OPTIONS,
            "staff_options":  cls.STAFF_OPTIONS,
            "active_tab":     tab,
            "active_period":  period,
            "active_staff":   staff,
            "columns":        cls.REVENUE_COLUMNS,
            "rows":           rows,
            "summary_row":    summary_row,
            "bar_max":        61200,
            "table_summary":  summary,
            "period_label":   "March 2026",
        }

    @classmethod
    def get_catalog_context(cls, *, category_pk: Optional[int] = None) -> Dict[str, Any]:
        active_category = next(
            (c for c in cls.CATALOG_CATEGORIES if c["pk"] == category_pk),
            cls.CATALOG_CATEGORIES[0],
        )
        return {
            "categories":      cls.CATALOG_CATEGORIES,
            "active_category": active_category,
            "items":           cls.CATALOG_ITEMS.get(active_category["pk"], []),
        }
