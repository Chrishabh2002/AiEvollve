# Agent Core Architecture & Lifecycle Specification

## A. Agent Lifecycle Model

The Agent Lifecycle is a finite state machine (FSM) managed by the Kernel. Transitions are event-driven and atomic.

### States
1.  **CREATED**: Initial state. Identity defined, memory initialized, but not yet scheduled.
2.  **IDLE**: Active and waiting for tasks. Connected to the message bus.
3.  **DELIBERATING**: Engaged in a discussion thread. Contributing to strategy/planning but not executing code.
4.  **EXECUTING**: Performing a specific task (running tools, writing code). Exclusive lock on execution resources.
5.  **AWAITING_REVIEW**: Work completed, waiting for peer/kernel validation.
6.  **FAILED**: Task execution failed or validation rejected the artifact.
7.  **QUARANTINED**: Suspended due to repeated failures or policy violations.
8.  **RETIRED**: Permanently archived.

### Valid Transitions & Triggers

| From | To | Trigger |
| :--- | :--- | :--- |
| *null* | **CREATED** | `Kernel.spawn_agent()` called. |
| **CREATED** | **IDLE** | Initialization checks passed. |
| **IDLE** | **DELIBERATING** | Invited to a Thread or `Self.join_thread()`. |
| **IDLE** | **EXECUTING** | Task assigned via Consensus or Direct Order. |
| **DELIBERATING** | **EXECUTING** | Consensus reached, task allocated to self. |
| **DELIBERATING** | **IDLE** | Thread concludes, task assigned to *others*. |
| **EXECUTING** | **AWAITING_REVIEW** | Task output produced, `Kernel.submit()` called. |
| **EXECUTING** | **FAILED** | Unhandled exception or timeout. |
| **AWAITING_REVIEW** | **IDLE** | Artifact accepted (+Reputation). |
| **AWAITING_REVIEW** | **FAILED** | Artifact rejected (-Reputation). |
| **FAILED** | **IDLE** | Error logged, state reset (with Reputation penalty). |
| **FAILED** | **QUARANTINED** | Consecutive failure limit exceeded. |
| **QUARANTINED** | **IDLE** | Manual override or time-based probation expiry. |
| **QUARANTINED** | **RETIRED** | Max recovery attempts exceeded. |
| *Any* | **RETIRED** | `Kernel.deprecate()` or Reputation < 0.1. |

---

## B. Agent Internal State

An agent is an object persisted in the database.

### 1. Kernel-Owned State (Immutable by Agent)
*   **UUID**: Unique 128-bit identifier.
*   **RoleDefinition**: `enum` (e.g., `ARCHITECT`, `CODER_PYTHON`).
*   **CreationTimestamp**: ISO-8601.
*   **CurrentState**: One of the FSM states above.
*   **GlobalReputation**: Float `0.0 - 1.0`.
*   **Permissions**: Bitmask of allowed Tool capabilities.

### 2. Agent-Owned State (Mutable via Kernel API)
*   **WorkingContext**: JSON blob. Current "thought process", scratchpad notes.
*   **PreferenceWeights**: Map<String, Float>. Learned biases (e.g., `{"testing_framework": "pytest": 0.9, "verbose_logging": 0.4}`).
*   **ActionLog**: List of recent Tool IDs used.

### 3. Ephemeral Runtime State (In-Memory Only)
*   **ActiveThreadID**: Current discussion channel.
*   **TaskTimeout**: Countdown timer for current execution.
*   **LLMContextBuffer**: Rolling window of recent tokens (managed by LLM client).

---

## C. Memory Architecture

### 1. Working Memory (Short-Term)
*   **Scope**: Bound to the *current* Thread or Task.
*   **Content**: System Prompt + Role + Thread History + Scratchpad.
*   **Eviction Policy**: FIFO on Thread History once token limit approached. Summary compressed into "Notes" before eviction.
*   **Reset**: Cleared upon transition to **IDLE**.

### 2. Episodic Memory (Long-Term / RAG)
*   **Storage**: Vector Database (e.g., Qdrant/Pinecone/pgvector).
*   **Schema**:
    ```json
    {
      "id": "uuid",
      "agent_id": "uuid",
      "timestamp": "iso-date",
      "type": "DECISION | ERROR | SUCCESS",
      "content": "Description of what happened...",
      "embedding": [float, ...],
      "metadata": {
        "task_type": "refactor",
        "outcome_score": 0.85,
        "related_files": ["main.py"]
      }
    }
    ```
*   **Permissions**:
    *   **Write**: Agent can write to its own memory partition.
    *   **Read**: Agent can search its own partition AND "Public Lessons" (verified successes from high-rep agents).
    *   **No-Read**: Cannot read private memories of other agents.

### 3. Influence Mechanism
*   **Retrieval**: Before responding, System executes `query_memory(current_context, top_k=3)`.
*   **Inject**: Retrieved memories are injected into the System Prompt as "Relevant Past Experiences".
*   **Bias Drift**: To avoid lock-in, the Kernel injects a random "Devil's Advocate" memory (counter-example) with 10% probability.

---

## D. Reputation System

Reputation is the currency of trust and influence. It is strictly numeric and managed by the Kernel.

### Initialization
*   **Base Score**: 0.5 (Neutral).
*   **Specialized Roles**: May start higher (0.6) if spawned for a critical shortage.

### Dynamics
| Action | Impact | Logic |
| :--- | :--- | :--- |
| **Artifact Acceptance** | **+0.05** | Passed CI/CD + Peer Review. |
| **Consensus Winner** | **+0.02** | Idea adopted by group vote. |
| **Artifact Rejection** | **-0.05** | Failed Peer Review (logical errors). |
| **Execution Failure** | **-0.10** | Crashed build / Invalid Syntax (objective failure). |
| **Misbehavior** | **-0.20** | Hallucinated file / Tried forbidden tool. |

### Influence on System
1.  **Voting Weight**: `VotePower = 1 + (Reputation - 0.5) * 2`. (Rep 1.0 = 2.0 votes, Rep 0.0 = 0.0 votes).
2.  **Task Assignment**: High-criticality tasks require `Reputation > 0.8`.
3.  **Consensus Trust**: "Super-Consensus" (immediate approval) is possible if supporting agents have `avg(Reputation) > 0.9`.

### Decay & Recovery
*   **Decay**: -0.01 per week of inactivity (prevents stagnation).
*   **Recovery Cap**: Agents in **QUARANTINED** state cannot gain Rep > 0.5 until probation ends.

---

## E. Agent Spawn & Retirement Logic

### Spawning
*   **Authority**: ONLY the Kernel can spawn agents.
*   **Triggers**:
    1.  **Load-Based**: `QueueLength > 5` for specific role -> Spawn `Junior` instance.
    2.  **Specialization**: New domain detected (e.g., "Rust code found") -> Spawn `Rust_Expert`.
    3.  **Evolution**: Validated success pattern -> Clone high-performing agent (copy weights/biases).
*   **Hard Caps**:
    *   `GlobalLimit`: 100 agents (prevent resource exhaustion).
    *   `RoleLimit`: Max 10 per role type.

### Retirement
*   **Conditions**:
    1.  **Obscelence**: `Reputation < 0.2` for > 7 days.
    2.  **Redundancy**: `IdleTime > 30 days` and `RoleCount > 2`.
    3.  **Instability**: `ErrorRate > 50%`.
*   **Process**:
    1.  State -> **RETIRED**.
    2.  Episodic Memory -> Archived to "Legacy Knowledge" (read-only for others).
    3.  Execution Resources -> Reclaimed.

---

## F. Failure & Misbehavior Handling

### Definitions
*   **Failure**: Unintentional error. (e.g., valid code fails a unit test, API timeout).
*   **Misbehavior**: Violation of protocol. (e.g., calling `rm -rf /`, attempting to modify Kernel code, infinite loop in reasoning).

### Handling Pipeline
1.  **Detection**:
    *   **Failure**: Detected by CI/CD pipeline or Tool return code.
    *   **Misbehavior**: Detected by Kernel Policy Middleware (static analysis of tool calls).

2.  **Penalties**:
    *   **Failure**: `Reputation -= 0.1`. Retry allowed (max 3).
    *   **Misbehavior**: `Reputation -= 0.2`. Immediate process kill.

3.  **Quarantine / Lockout**:
    *   **Trigger**: 3 consecutive Failures or 1 Misbehavior event.
    *   **Action**: State -> **QUARANTINED**.
    *   **Diagnostics**: Kernel spawns a "Debugger" agent to analyze the quarantined agent's logs.
    *   **Probation**: Must pass a set of synthetic "Safety Tests" to return to **IDLE**.
