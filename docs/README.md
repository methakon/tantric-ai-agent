# Tantric AI Agent — Documentation

This directory is the canonical documentation set for the project. It is
organised around the lifecycle of a standard project: everything you need
**before** you start the system (prerequisites, build, configuration) and
everything you need **after** it is running (operation, APIs, troubleshooting).

The documentation was reconstructed by auditing the source tree directly
(back-tracking from code → behaviour → docs), so each statement traces to a
specific file. Where source and prior prose disagreed, the source wins.

---

## Reading order

### Pre-start (before the system runs)

| Doc | Purpose |
|-----|---------|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | What the system is, the three processes, and how data flows. Read this first. |
| [`SETUP.md`](SETUP.md) | Prerequisites, Swiss Ephemeris build, C++ engine + gateway build, Python venv, database init. |
| [`CONFIGURATION.md`](CONFIGURATION.md) | Every environment variable, who reads it, and its default. |
| [`INTENT_CLASSIFIER.md`](INTENT_CLASSIFIER.md) | Tier-4 tiny ML intent router (mixed bn/en) that makes chat routing generalise. |

### Post-start (while the system runs)

| Doc | Purpose |
|-----|---------|
| [`RUNBOOK.md`](RUNBOOK.md) | Start/stop sequence, health checks, common failures and fixes. |
| [`API.md`](API.md) | HTTP/WebSocket routes and the internal gateway↔bridge IPC protocol. |
| [`SECURITY.md`](SECURITY.md) | Auth, encryption, rate limiting, file-ingestion sandbox, secret handling. |
| [`TESTING.md`](TESTING.md) | How to build and run every test suite. |

### Domain & provenance

| Doc | Purpose |
|-----|---------|
| [`../TANTRIC_AI_AGENT_ROADMAP.md`](../TANTRIC_AI_AGENT_ROADMAP.md) | Full blueprint, phases, and the esoteric/astrological domain model. |
| [`lineage_sources.md`](lineage_sources.md) | Source register and quoting policy for `src/lineage_wisdom.cpp`. |
| [`kundali/`](kundali/) | Standalone kundali-analysis research workspace (self-contained Python). |
| [`research/`](research/) | Research datasets (e.g. `bamakhepa_tarapith_knowledge.json`). |

---

## System at a glance

A three-process hybrid: a dependency-free C++20 HTTP/WebSocket **gateway**, a
Python **IPC bridge** (auth authority + service backend over a Unix domain
socket), and a short-lived C++20 **engine** binary invoked as a subprocess for
sidereal charts, sacred-geometry SVG, mantra safety checks, and lineage text.

```
Browser ──HTTP/WS──> tantric_gateway (C++, :8090)
                          │  Unix domain socket (/tmp/hermes_esoteric.sock)
                          ▼
                     ipc_bridge.py --serve  (Python auth + services)
                          │  subprocess
                          ▼
                     tantric_engine  (C++ --yantra | --safety | --lineage)
```

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full picture.
