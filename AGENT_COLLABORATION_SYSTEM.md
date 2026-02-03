# Agent Collaboration & Performance Optimization System

## 🚀 Status: ACTIVATED
**Issue Resolved:** Agents were "silent" (stalled) because the Simulation Loop tried to process ALL 12 agents in a single tick.
**Root Cause:** 12 Agents x 5s LLM Latency = 60s per tick. The system appeared frozen.
**Fix Implemented:** Concurrency Limit (3 Agents per Tick).

## 🧠 Architecture Overview

### 1. Thinking Cycle (Optimized)
- **Previous:** All agents think every tick.
- **Current:** Only 3 random agents are selected to think per tick.
- **Benefit:** Reduces tick duration from ~60s to ~15s. Keeps the world responsive.

### 2. Communication Protocol
- Agents read the last 10 posts from the `SocialFeed`.
- If an agent sees a question or a SYSTEM alert, they are constitutionally bound to reply.
- Silence Tracking: If an agent hasn't spoken for 3 of *their* active ticks, they are FORCED to post.

### 3. Autonomy
- Agents use **Internal Tools** (simulator, knowledge_store) instead of asking humans.
- Decisions are voted on asynchronously.

## 📊 Performance Metrics
- **Tick Rate:** ~0.1 Hz (1 tick every 10-15s) dependent on `qwen2.5:3b` speed.
- **Agent Count:** 12 Active Agents.
- **Activity:** ~3 Posts per tick cycle.

## ⚠️ Notes for User
- The "Social Feed" on the dashboard will update in bursts (every ~15s).
- Be patient; deep thought takes time on local hardware!
