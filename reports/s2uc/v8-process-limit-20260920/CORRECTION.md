# Preserved initial attempt

The allocation-only case completed and is retained as the enforcement evidence.
The two product cases exited before running V8: `-I` hid the installed user-site
NumPy package, causing `ModuleNotFoundError`. Both traces, code, plans and raw
samples are retained unchanged; neither is a successful product closure.

Correction in a separate sibling report: remove only `-I`, retain `-S` and the
blocking pre-import admission. Explicit `site.main()` remains after checked Job
Object membership/limit. Repeat only success and injected-MemoryError cases.
Do not repeat the already valid allocation case or prior memory-measurement cases.
