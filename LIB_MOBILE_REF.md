# Library Mobile Refactoring Specification

This document contains precise technical tasks to fix mobile responsiveness issues in the `codex_django` core.

---

## 1. Core Layout Patches

### [LAYOUT] Sidebar & Content Offset
- **Target File:** `src/codex_django/showcase/static/showcase/cabinet/css/base/layout.css`
- **Issue:** `.cab-main` has `margin-left: 60px` causing horizontal overflow on mobile.
- **Fix:**
    - Add media query `@media (max-width: 768px)`.
    - Set `.cab-main { margin-left: 0 !important; }`.
    - Set `.cab-sidebar { transform: translateX(-100%); }` (if not already handled) and ensure toggle works.

### [TABLES] Card-Mode for Data Tables
- **Target File:** `src/codex_django/cabinet/templates/cabinet/components/data_table.html`
- **Issue:** Horizontal scrolling `<table>` is unusable on mobile.
- **Fix:**
    - Implement a mobile-only card container.
    - Loop through `table.rows` and render each row as a `.cab-card`.
    - Use `column.label` as a field header inside the card.
    - Hide the main `<table>` on mobile.

### [MODALS] Full-Screen Mobile Modals
- **Target File:** `src/codex_django/showcase/static/showcase/cabinet/css/cabinet.css`
- **Issue:** Fixed-width centered modals waste screen space.
- **Fix:**
    - `@media (max-width: 576px)`:
    - `.modal-dialog { margin: 0; max-width: 100%; width: 100%; }`
    - `.modal-content { border: 0; border-radius: 0; min-height: 100vh; }`
    - `.modal-footer { flex-direction: column-reverse; gap: 10px; }`
    - `.modal-footer button { width: 100%; margin: 0 !important; }`

### [WIDGETS] KPI Fluid Typography
- **Target File:** `src/codex_django/cabinet/templates/cabinet/widgets/kpi.html`
- **Issue:** Hardcoded `1.9rem` size.
- **Fix:** Use `font-size: clamp(1.2rem, 5vw, 1.9rem);`.

---

## 2. Component Promotion (Import from Lily Project)

### [COMPONENTS] Universal Luxury Cards
- **Task:** Create `src/codex_django/cabinet/templates/cabinet/components/card_grid.html`.
- **Logic:** Port the card grid pattern from the Lily project to the library as a standard template.

### [CSS] Staff & Entity Cards
- **Task:** Create `src/codex_django/showcase/static/showcase/cabinet/css/components/cards.css`.
- **Logic:** Port `staff_cards.css` styles to the library core.
