const API_ROOT = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
const API_BASE = `${API_ROOT}/api/world`;

// Helper function with retry logic
async function fetchWithRetry(url: string, retries = 2): Promise<Response> {
    for (let i = 0; i < retries; i++) {
        try {
            const res = await fetch(url, { cache: 'no-store' });
            return res;
        } catch (error) {
            if (i === retries - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1s before retry
        }
    }
    throw new Error('Max retries reached');
}

export async function fetchSocialTimeline() {
    try {
        const res = await fetchWithRetry(`${API_ROOT}/api/social/timeline?include_replies=true`);
        if (!res.ok) throw new Error('Failed to fetch timeline');
        return res.json();
    } catch (error) {
        console.error('Timeline fetch error:', error);
        return []; // Return empty array on error
    }
}

export async function fetchHealth() {
    try {
        const res = await fetchWithRetry(`${API_BASE}/health`);
        if (!res.ok) throw new Error('Failed to fetch health');
        return res.json();
    } catch (error) {
        console.error('Health fetch error:', error);
        return { status: 'error', tick: 0 };
    }
}

export async function fetchAgents() {
    try {
        const res = await fetchWithRetry(`${API_BASE}/agents`);
        if (!res.ok) throw new Error('Failed to fetch agents');
        return res.json();
    } catch (error) {
        console.error('Agents fetch error:', error);
        return [];
    }
}

export async function fetchFeed() {
    try {
        const res = await fetchWithRetry(`${API_BASE}/feed`);
        if (!res.ok) throw new Error('Failed to fetch feed');
        return res.json();
    } catch (error) {
        console.error('Feed fetch error:', error);
        return [];
    }
}

export async function fetchDecisions() {
    try {
        const res = await fetchWithRetry(`${API_BASE}/decisions`);
        if (!res.ok) throw new Error('Failed to fetch decisions');
        return res.json();
    } catch (error) {
        console.error('Decisions fetch error:', error);
        return [];
    }
}

export async function fetchDecisionDetail(id: string) {
    try {
        const res = await fetchWithRetry(`${API_BASE}/decisions/${id}`);
        if (!res.ok) throw new Error('Failed to fetch decision detail');
        return res.json();
    } catch (error) {
        console.error('Decision detail fetch error:', error);
        return null;
    }
}

export async function fetchPlans() {
    try {
        const res = await fetchWithRetry(`${API_BASE}/plans`);
        if (!res.ok) throw new Error('Failed to fetch plans');
        return res.json();
    } catch (error) {
        console.error('Plans fetch error:', error);
        return [];
    }
}

export async function fetchExecutionStats() {
    try {
        const res = await fetchWithRetry(`${API_BASE}/plans/stats/execution`);
        if (!res.ok) throw new Error('Failed to fetch execution stats');
        return res.json();
    } catch (error) {
        console.error('Execution stats fetch error:', error);
        return {
            total_executions: 0,
            successes: 0,
            failures: 0,
            success_rate: 0,
            active_plans: 0,
            completed_plans: 0,
            failed_plans: 0
        };
    }
}

