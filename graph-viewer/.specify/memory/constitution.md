<!--
Sync Impact Report
Version change: 1.0.0 -> 1.1.0
Modified principles:
- II. Minimal Frontend Stack (MUST): resolved frontend stack as Streamlit
Added sections: None
Removed sections: None
Templates requiring updates:
- Updated: .specify/templates/plan-template.md
- Reviewed, no change required: .specify/templates/spec-template.md
- Reviewed, no change required: .specify/templates/tasks-template.md
- Reviewed, no change required: .specify/templates/checklist-template.md
- Pending: .specify/templates/commands/*.md does not exist in this repo
Follow-up TODOs: None
-->
# Graph Viewer Constitution

## Core Principles

### I. Performance Is a Product Boundary (MUST)
The graph viewer MUST render and support interaction with graphs of at least
5,000 nodes without perceptible degradation: pan and zoom remain fluid, and the
UI MUST not freeze during parsing, layout, render, or viewport interaction.

Any rendering, layout, state, or dependency decision MUST preserve this bound.
Plans MUST define measurable performance checks for 5,000-node graphs before
implementation. Work that risks this limit MUST document the tradeoff and
mitigation before being accepted.

Rationale: graph-viewer is useful only if real graph exploration remains
interactive at meaningful scale.

### II. Minimal Frontend Stack (MUST)
The application frontend MUST be built with Streamlit. Streamlit is the UI
shell for graph upload/input, validation feedback, controls, and viewer
composition. This stack requirement does not relax the 5,000-node performance
gate; any Streamlit integration or custom component strategy MUST preserve
fluid pan and zoom without freezing the UI.

Dependencies MUST be lightweight and necessary for graph viewing. Every new
runtime or build dependency MUST be justified in plan.md with expected value,
bundle/performance impact, and a rejected lighter alternative.

Rationale: heavy or unclear dependencies directly threaten startup time,
interaction latency, and maintainability.

### III. Isolated Testability (MUST)
Parsing, schema validation, graph data modeling, layout calculation, and render
preparation MUST be modular and testable without mounting the UI. Any change to
input parsing, validation, layout, or render-preparation logic MUST include
tests that exercise that logic in isolation.

UI tests can complement these tests, but they are not a substitute for isolated
tests of the underlying graph logic.

Rationale: correctness and performance issues in graph logic must be detectable
without fragile end-to-end workflows.

### IV. Layered Graph Architecture
Parsing, validated graph data model, layout, and render are separate layers with
explicit contracts. A layer MUST NOT depend on UI components. Render code
consumes layout/render view data; it MUST NOT parse raw input or mutate the
canonical graph model.

Cross-layer changes MUST update the corresponding contracts and tests.

Rationale: clear ownership makes the viewer evolvable and keeps
performance-critical code measurable.

### V. Schema-First Input Validation (MUST)
Node and edge JSON input MUST be validated against a schema before rendering
starts. Invalid input MUST produce actionable user-facing errors. Validation
errors MUST NOT be silently ignored, coerced without explanation, or deferred
until render time.

Rationale: malformed graph data must fail predictably before it can produce
broken layout, empty render output, or frozen interaction.

## Technical Constraints

- Plans MUST include a 5,000-node performance gate covering parse, layout,
  initial render, pan, and zoom.
- Feature specs MUST define expected behavior for invalid JSON, schema
  violations, missing nodes, duplicate identifiers, dangling edges, and empty
  graphs.
- Runtime graph logic MUST be organized so parsing, model, layout, and render
  preparation can be imported and tested independently of UI components.
- The frontend MUST use Streamlit. Any custom graph-rendering component or
  browser-side renderer integrated with Streamlit counts as a new dependency
  and MUST be justified in plan.md.
- New libraries MUST be listed in plan.md with purpose, expected
  size/performance impact, and lighter alternatives considered.

## Development Workflow and Quality Gates

- Constitution Check in every plan MUST pass before Phase 0 research and be
  rechecked after design.
- Tasks touching parsing, validation, data model, layout, or render preparation
  MUST include isolated tests in the same user-story slice or in foundational
  work.
- Performance-sensitive changes MUST include a reproducible check for
  5,000-node interaction.
- User-facing error reporting for invalid input MUST be covered by acceptance
  criteria or tests.
- Reviews MUST reject changes that couple parsing, model, layout, render, and
  UI without an explicit contract update.

## Governance
This constitution supersedes conflicting project guidance. Every spec, plan,
task list, and review MUST check compliance with these principles.

Amendments require a documented change to this file, a Sync Impact Report, and
updates to affected templates or runtime guidance. Versioning follows semantic
versioning: MAJOR for principle removals or incompatible governance changes,
MINOR for added or materially expanded principles or sections, and PATCH for
clarifications.

Compliance review is required at plan creation, after design, and before
marking work complete. Unresolved TODO items in this constitution are blockers
for implementation decisions that depend on them.

**Version**: 1.1.0 | **Ratified**: 2026-06-27 | **Last Amended**: 2026-06-27
