# Decision, Debate, and Consensus Engine Specification

## A. Decision Trigger Model

The **Decision Engine** is an event-driven subsystem managed by the Kernel. A "Decision" is a formal object in the database, distinct from a chat thread.

### 1. Trigger Types
*   **External Request**: User submits a new Requirement. -> Triggers `ScopeDefinition` decision.
*   **Agent Proposal**: Agent in a thread calls `propose_solution()`. -> Triggers `TechnicalReview` decision.
*   **Execution Failure**: Task fails with `UnrecoverableError`. -> Triggers `RecoveryStrategy` decision.
*   **Discovery**: Agent finds new information (e.g., API deprecation). -> Triggers `ArchitectureAdjustment` decision.

### 2. Scoping & Context
*   decisions are **Scoped** to a specific `ThreadID` and `TaskID`.
*   Global decisions (e.g., "Change Primary Language to Rust") trigger a broadcast to a specialized `ArchitectureCouncil` thread.
*   **Context Object**:
    ```json
    {
      "decision_id": "uuid",
      "proposal_id": "uuid",
      "scope": "LOCAL | GLOBAL",
      "deadline": "2023-10-27T10:00:00Z",
      "required_quorum": 0.6,
      "status": "OPEN"
    }
    ```

---

## B. Debate Structure

Debates are structured data exchanges, not free-form chat.

### 1. Submission Format (Structured Opinion)
Agents must submit opinions using the `submit_opinion` tool.
```json
{
  "outcome": "APPROVE | REJECT | AMEND",
  "rationale": "Markdown string explaining the logic...",
  "confidence": 0.0 - 1.0,
  "risks": [
    {"risk_type": "PERFORMANCE", "severity": "HIGH", "description": "O(n^2) loop"}
  ],
  "dependencies": ["uuid-of-previous-decision"]
}
```

### 2. The Debate Cycle
1.  **Proposal Phase**: Agent A posts a `Proposal` artifact.
2.  **Critique Phase**: Agents B, C, D submit `Opinion` objects (Critiques).
3.  **Rebuttal Phase**: Agent A posts a `Rebuttal` (Reply to Critiques).
4.  **Final Call**: Logic (Kernel or Lead Agent) freezes the thread for Voting.

### 3. Constraints
*   **Max Iterations**: 3 rounds of Critique/Rebuttal.
*   **Timeout**: 30 minutes wall-clock time per decision (configurable).

---

## C. Voting & Weighting System

Voting is the mechanism to quantify consensus.

### 1. Vote Cast
*   Vote = `{ agent_id, choice, weight_modifier }`
*   Choices: `YES`, `NO`, `BLOCK` (Veto).

### 2. Weighted Voting Logic
The raw vote of an agent is multiplied by their **Contextual Reputation**.
*   `BaseWeight = Agent.GlobalReputation`
*   `RoleBonus = 1.5` (if Decision Domain matches Agent Role, e.g., DBA voting on SQL Schema).
*   `VotePower = BaseWeight * RoleBonus`.

### 3. Quorum Requirements
*   **Minimum Participation**: > 50% of active agents in the thread.
*   **Minimum Power**: Sum of `VotePower` must exceed `Threshold_X`.

### 4. Definition of Consensus
*   **Simple Consensus**: > 51% of Weighted Votes are `YES` AND No `BLOCK` votes.
*   **Super-Consensus**: > 80% Weighted `YES` AND Average Confidence > 0.8.
*   **Forced Resolution**: If timeout reached, highest weighted group wins (unless vetoed).

---

## D. Consensus Resolution Algorithm

The Kernel executes this deterministic algorithm when the Voting Window closes:

```python
def resolve_consensus(votes):
    total_power = sum(v.power for v in votes)
    yes_power = sum(v.power for v in votes if v.choice == 'YES')
    block_votes = [v for v in votes if v.choice == 'BLOCK']

    # 1. Check Veto
    if block_votes:
        return {
            "result": "REJECTED",
            "reason": "VETO_EXERCISED",
            "blocking_agents": [v.agent_id for v in block_votes] # Penalty if veto was frivolous
        }

    # 2. Check Super-Consensus
    confidence_avg = avg(v.confidence for v in votes)
    if (yes_power / total_power > 0.8) and (confidence_avg > 0.8):
        return {"result": "ACCEPTED", "type": "SUPER_CONSENSUS"}

    # 3. Check Simple Consensus
    if (yes_power / total_power > 0.51):
        return {"result": "ACCEPTED", "type": "SIMPLE_MAJORITY"}

    # 4. Default
    return {"result": "REJECTED", "reason": "INSUFFICIENT_SUPPORT"}
```

*   **Minority Report**: All `NO` votes and their rationales are archived in `DecisionHistory` for future failure analysis.

---

## E. Deadlock & Conflict Resolution

Deadlock occurs when votes are split ~50/50 or repeated Vetoes occur.

### 1. Detection
*   Vote margin < 5%.
*   3 consecutive `REJECTED` outcomes on the same TopicID.

### 2. Resolution Strategies (Sequential Escalation)
1.  **Injection**: Kernel spawns a fresh `Senior_Architect` agent (templated with high 'Reasoning' stats) into the thread to break the tie.
2.  **Scope Reduction**: Kernel forces the Proposal to be split into two smaller sub-decisions.
3.  **Randomized Backoff**: Thread paused for 5 minutes; Memory injection of similar *successful* past decisions.
4.  **Abort**: If all fails, mark Task as `NEEDS_HUMAN_INTERVENTION`.

---

## F. Execution Authorization

A decision is just a plan. Execution Authorization allows *action*.

### 1. Transition to Execution
*   Trigger: `ConsensusResult == ACCEPTED`.
*   Action: Kernel generates a signed `ExecutionToken`.

### 2. Token Metadata
*   `TokenID`: UUID.
*   `AuthorizedScope`: List of allowed FilePaths or API domains (e.g., `["src/backend/*", "aws:s3:*"]`).
*   `Budget`: Max cost in compute/dollars for this specific implementation.
*   `RollbackHash`: Pointer to the git commit hash BEFORE this execution starts.

### 3. Rollback Logic
*   If execution fails, the `Planner` reads the `RollbackHash` and executes `git reset --hard <hash>`.

---

## G. Safety & Anti-Echo-Chamber Controls

### 1. Mandatory Dissent (Red Teaming)
*   If a Proposal reaches 100% agreement instantly:
    *   Kernel **BLOCKS** execution.
    *   Kernel spawns a temporary `Devil's Advocate` agent.
    *   Instruction: "Find 3 flaws in this plan."
    *   Re-vote is forced after the critique.

### 2. Reputation Diversity
*   A quorum is INVALID if all voters share the exact same `Role` or `Bias` settings.
*   Requirement: At least 2 different roles must vote (e.g., 1 Coder + 1 Tester).

### 3. Randomized Audits
*   5% of "Simple Consensus" decisions are flagged for "Deep Review."
*   A separate "Auditor" agent reviews the decision log asynchronously. If flaws are found, the original voters suffer a **Reputation Penalty**.
