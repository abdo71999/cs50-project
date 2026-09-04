# Deferred Engineering Backlog

These improvements are intentionally postponed so the first working version can be completed one learning step at a time.

- Replace broad `except Exception` handling with expected CSV exceptions or a custom data-processing exception.
- Return appropriate HTTP error statuses and render user-friendly HTML error pages.
- Set a maximum upload size.
- Delete replaced uploads and expire abandoned temporary files.
- Remove unused dependencies and pin the dependencies the project actually uses.
- Extract repeated session and upload-path lookup after the shared abstraction becomes clear.
- Add automated tests with `pytest` so validation and regression behavior no longer require repeated manual testing.

Review this list before considering the project production-ready.
