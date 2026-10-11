# ScopeGuard workbench redesign

References reviewed before implementation, 11 October 2026:

- [Sayef Mahmud / Pixel Navy: Project management dashboard UI](https://dribbble.com/shots/18934128-Project-management-dashboard-UI): persistent workspace rail and deliberately grouped controls.
- [MultiQoS: Project and Task Management Dashboard Design](https://www.behance.net/gallery/176547795/Project-and-Task-Management-Dashboard-Design): compact overview with a clear division between navigation and work.

These informed hierarchy, not copied assets. This is a working product interface; the pinned taste-skill was applied contextually rather than forcing a marketing layout onto an editing tool.

The new design uses a cool paper workbench, side-by-side source editors, real decision counts, request/reference pairs and radio-based decisions. All commercial decisions remain manual. No model, semantic understanding, confidence score or effort estimate was added. Currency formatting and export behavior are unchanged.

Radio groups replace the old native selectors and support keyboard arrow navigation. Light/dark tokens, visible focus, reduced motion and narrow single-column layouts are included. All text is rendered safely by Vue. Existing local-storage state remains compatible.

`tests/browser.py` checks the actual workflow, including pricing, exact clipboard/download, persistence, stale-source protection, reset, inert HTML and mobile overflow. `artifacts/axe.json` records zero automated violations in light and dark modes. Automated checks do not replace assistive-technology testing.
