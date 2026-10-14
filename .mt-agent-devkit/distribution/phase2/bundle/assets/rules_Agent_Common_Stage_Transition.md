# Agent Common Stage Transition

## 5. Runtime-State Handoff (implementer & reviewer roles)

Before signaling completion, write any needed Memory, Working Record, retrospective,
telemetry, or pipeline-state update to its runtime path. These are local runtime state:
never `git add`, commit, or push them on a product branch in either mode. Report stage
completion after the local handoff is complete. A project that needs versioned agent
knowledge requires a separately designed repository and branch policy.

---

