<!-- DOC_TYPE: GUIDE -->

# Руководство по Cabinet

## Когда Использовать

Используйте `cabinet`, когда нужен переиспользуемый dashboard shell с навигацией, виджетами и типизированными компонентами страниц. Cabinet предоставляет layout и структурные шаблоны; ваши feature apps добавляют навигационные записи и строят данные страниц через типизированные контракты.

## Установка

Добавьте в `INSTALLED_APPS` и подключите context processor:

```python
INSTALLED_APPS = [
    ...
    "codex_django.cabinet",
    "cabinet",  # ваш project-level cabinet app
]

TEMPLATES = [{
    "OPTIONS": {
        "context_processors": [
            ...
            "codex_django.cabinet.context_processors.cabinet",
        ]
    }
}]
```

## Регистрация Feature

Создайте `cabinet.py` в любом установленном app. `CabinetConfig.ready()` обнаруживает его автоматически через `autodiscover_modules("cabinet")`.

```python
# features/booking/cabinet.py
from codex_django.cabinet import declare, TopbarEntry, SidebarItem, Shortcut

# Staff пространство
declare(
    space="staff",
    module="booking",
    topbar=TopbarEntry(
        group="services",
        label="Бронирование",
        icon="bi-calendar-check",
        url="/cabinet/booking/",
        order=10,
    ),
    sidebar=[
        SidebarItem(label="Расписание",  url="booking:schedule",   icon="bi-calendar3"),
        SidebarItem(label="Новая запись", url="booking:new",        icon="bi-plus-circle"),
        SidebarItem(label="Ожидают",     url="booking:pending",    icon="bi-hourglass-split",
                    badge_key="pending_count"),
    ],
    shortcuts=[
        Shortcut(label="Новая", url="booking:new", icon="bi-plus"),
    ],
)
```

## Активный Модуль во View

Context processor читает `request.cabinet_module`, чтобы определить какой sidebar показывать.
Установите его в начале любого cabinet view:

```python
def schedule_view(request):
    request.cabinet_module = "booking"
    ...
    return render(request, "booking/schedule.html", context)
```

Если не установлено, модуль определяется автоматически из URL namespace (`request.resolver_match.app_name`),
с финальным fallback на `"admin"`.

## Переходы Между Пространствами

Context processor добавляет дефолтные URL для topbar:

- `cabinet_site_url` — ссылка на публичный сайт, по умолчанию `/`.
- `cabinet_client_switch_url` — переход из staff/admin кабинета в клиентский кабинет, по умолчанию `/cabinet/my/`.
- `cabinet_staff_switch_url` — переход из клиентского кабинета в staff/admin пространство, по умолчанию `/cabinet/`.
- `cabinet_login_url` и `cabinet_logout_url` — безопасные ссылки входа/выхода.

Их можно переопределить настройками:

```python
CODEX_CABINET_SITE_URL = "/"
CODEX_CABINET_CLIENT_URL_NAME = "cabinet:client_home"  # или literal path
CODEX_CABINET_STAFF_URL_NAME = "cabinet:dashboard"
CODEX_CABINET_LOGIN_URL_NAME = "account_login"
CODEX_CABINET_LOGOUT_URL_NAME = "account_logout"
```

Если URL name не подключен в проекте, библиотека использует fallback path и
topbar не падает на `NoReverseMatch`.

## Использование Компонента Страницы

Постройте типизированный контракт во view, передайте его в шаблон и отрендерите компонент через шаблонный include.

### Таблица Данных

```python
# view
from codex_django.cabinet import DataTableData, TableColumn, TableFilter, TableAction

def appointments_view(request):
    request.cabinet_module = "booking"
    table = DataTableData(
        columns=[
            TableColumn(key="client", label="Клиент", bold=True),
            TableColumn(key="date",   label="Дата"),
            TableColumn(key="status", label="Статус"),
        ],
        rows=list(Appointment.objects.values("client", "date", "status", "detail_url")),
        filters=[
            TableFilter(key="pending",   label="Ожидают",    value="pending"),
            TableFilter(key="confirmed", label="Подтверждены", value="confirmed"),
        ],
        actions=[TableAction(label="Открыть", url_key="detail_url", icon="bi-eye")],
        search_placeholder="Поиск...",
    )
    return render(request, "booking/appointments.html", {"table": table})
```

```django
{# booking/appointments.html #}
{% extends "cabinet/base_cabinet.html" %}
{% block content %}
  {% templatetag openblock %} include "cabinet/components/data_table.html" with table=table {% templatetag closeblock %}
  {% templatetag openblock %} include "cabinet/includes/_modal_base.html" {% templatetag closeblock %}
{% endblock %}
```

### Сетка Календаря

Columns и rows — это что угодно: мастера, кабинеты, дни недели.
Backend вычисляет `CalendarSlot.span` из длительности; шаблон только рендерит.

```python
from codex_django.cabinet import CalendarGridData, CalendarSlot

# 30-минутные слоты с 08:00 до 20:00
rows = [f"{h}:{m:02d}" for h in range(8, 20) for m in (0, 30)]

calendar = CalendarGridData(
    cols=["Мастер 1", "Мастер 2", "Мастер 3"],
    rows=rows,
    events=[
        CalendarSlot(
            col=0, row=2, span=2,       # индекс колонки, индекс строки, длительность/slot_size
            title="Иван П.", subtitle="Стрижка",
            color="#6366f1", url="/booking/42/",
        ),
    ],
    slot_height_px=40,
    new_event_url="/booking/new/",      # hx-get при клике на пустой слот
)
return render(request, "booking/schedule.html", {"calendar": calendar})
```

```django
{% extends "cabinet/base_cabinet.html" %}
{% block content %}
  {% templatetag openblock %} include "cabinet/components/calendar_grid.html" with calendar=calendar {% templatetag closeblock %}
  {% templatetag openblock %} include "cabinet/includes/_modal_base.html" {% templatetag closeblock %}
{% endblock %}
```

### Сетка Карточек

```python
from codex_django.cabinet import CardGridData, CardItem

cards = CardGridData(
    items=[
        CardItem(
            id=str(c.pk),
            title=c.full_name,
            subtitle=c.category,
            avatar=c.initials,
            url=f"/cabinet/clients/{c.pk}/",
            meta=[("bi-telephone", c.phone)],
        )
        for c in Client.objects.all()
    ],
    search_placeholder="Поиск клиентов...",
)
```

```django
{% templatetag openblock %} include "cabinet/components/card_grid.html" with cards=cards {% templatetag closeblock %}
```

### Split Panel

```python
from codex_django.cabinet import SplitPanelData, ListRow

panel = SplitPanelData(
    items=[
        ListRow(id=str(c.pk), primary=c.subject, secondary=c.last_message[:60])
        for c in conversations
    ],
    detail_url="/cabinet/conversations",  # добавляет /<id> при клике
    empty_message="Выберите переписку",
)
```

```django
{% templatetag openblock %} include "cabinet/components/split_panel.html" with panel=panel {% templatetag closeblock %}
```

## Страницы Отчетов

Для аналитических страниц используйте data-driven контракт: проект собирает
бизнес-данные, а библиотека рендерит общий premium reports UI.

```python
from codex_django.cabinet import (
    ChartAxisData,
    ChartDatasetData,
    ReportChartData,
    ReportPageData,
    ReportTabData,
    ReportTableData,
    TableColumn,
    resolve_report_period,
)

def reports_view(request):
    request.cabinet_module = "analytics"
    period = resolve_report_period(request.GET.get("period"))

    report = ReportPageData(
        title="Отчеты",
        summary="Выручка и объем записей за выбранный период.",
        active_tab=request.GET.get("tab", "revenue"),
        active_period=period.key,
        tabs=[
            ReportTabData(key="revenue", label="Выручка", icon="bi-currency-dollar"),
            ReportTabData(key="services", label="Услуги", icon="bi-stars"),
        ],
        period_options=[
            ReportTabData(key="week", label="Неделя"),
            ReportTabData(key="month", label="Месяц"),
            ReportTabData(key="quarter", label="Квартал"),
        ],
        period_label=f"{period.date_from:%d.%m.%Y} - {period.date_to:%d.%m.%Y}",
        table=ReportTableData(
            columns=[
                TableColumn(key="label", label="День", bold=True),
                TableColumn(key="revenue", label="Выручка", align="right"),
                TableColumn(key="volume", label="Объем", align="right"),
            ],
            rows=[{"label": "01.04", "revenue": "12 000", "volume": 4}],
            summary_row={"label": "Итого", "revenue": "12 000", "volume": 4},
        ),
        chart=ReportChartData(
            chart_id="revenueVolumeChart",
            title="Динамика",
            labels=["01.04"],
            type="bar",
            datasets=[
                ChartDatasetData(label="Объем", data=[4], type="bar", y_axis_id="y"),
                ChartDatasetData(label="Выручка", data=[12000], type="line", y_axis_id="y1"),
            ],
            axes=[
                ChartAxisData(id="y", position="left", label="Объем"),
                ChartAxisData(id="y1", position="right", label="Выручка", draw_on_chart_area=False),
            ],
        ),
    )
    return render(request, "cabinet/reports/page.html", {"report": report})
```

Библиотека не знает про `Order`, `Service`, `Appointment` или `Product`.
Эти запросы остаются в проектном selector/service слое.

## Клиентское Пространство

Зарегистрируйте отдельный вызов `declare(space="client", ...)` и наследуйтесь от `base_client.html`:

```python
declare(
    space="client",
    module="booking",
    sidebar=[
        SidebarItem(label="Мои записи", url="booking:my_bookings",
                    icon="bi-calendar2-check"),
    ],
)
```

```django
{# my_appointments.html #}
{% extends "cabinet/base_client.html" %}
{% block content %}
  {% templatetag openblock %} include "cabinet/components/data_table.html" with table=table {% templatetag closeblock %}
{% endblock %}
```

CSS-токены клиентского пространства переопределяются независимо через `.cab-wrapper--client { --cab-* }` в `theme/tokens.css` проекта.

## Доступные Компоненты

| Шаблон | Контракт | Для чего |
|--------|---------|---------|
| `cabinet/components/data_table.html` | `DataTableData` | Таблицы с фильтрами |
| `cabinet/components/calendar_grid.html` | `CalendarGridData` | Сетки расписания |
| `cabinet/components/card_grid.html` | `CardGridData` | Карточки клиентов/объектов |
| `cabinet/components/list_view.html` | `ListViewData` | Простые списки |
| `cabinet/components/split_panel.html` | `SplitPanelData` | Переписка/detail views |
| `cabinet/reports/page.html` | `ReportPageData` | Аналитические отчеты |

## Точки Входа Runtime

- `codex_django.cabinet`
- `codex_django.cabinet.selector`
- `codex_django.cabinet.redis`

## Связанные Разделы

- Архитектура: [Модуль Cabinet](../architecture/cabinet.md)
- API reference: [Cabinet Public API](../api/cabinet.md)
- Внутренности: [Cabinet Internal Modules](../api/internal/cabinet.md)
