import sys
import os
import argparse

# Ensure we can import kernel modules
sys.path.append(os.getcwd())

from kernel.core import Kernel

def setup_demo_kernel():
    """
    Initializes a kernel and runs a few ticks to populate data for the CLI demo.
    """
    k = Kernel()
    k.spawn_agent("Alice", "Architect", "Visionary")
    k.spawn_agent("Bob", "Engineer", "Pragmatic")
    k.spawn_agent("Charlie", "QA", "Critical")
    
    # Run a few ticks to generate state
    for _ in range(5):
        k.tick()
        
    return k

def print_table(headers, rows):
    if not rows:
        print("No data found.")
        return

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    # Formatting string
    fmt = "  ".join([f"{{:<{w}}}" for w in col_widths])

    # Print Header
    print("-" * (sum(col_widths) + len(col_widths) * 2))
    print(fmt.format(*headers))
    print("-" * (sum(col_widths) + len(col_widths) * 2))

    # Print Rows
    for row in rows:
        print(fmt.format(*[str(v) for v in row]))
    print("-" * (sum(col_widths) + len(col_widths) * 2))

def cmd_status(k):
    status = k.introspection.get_system_status()
    print("\nSYSTEM STATUS")
    print("=" * 20)
    print(f"Current Tick:  {status['tick']}")
    print(f"Agent Count:   {status['agent_count']}")
    print(f"Decisions:     {status['decision_count']}")
    print(f"Active Plans:  {status['active_plans']}")
    print("=" * 20)

def cmd_agents(k):
    agents = k.introspection.get_agents()
    print("\nAGENTS")
    
    headers = ["ID", "Name", "Role", "State", "Reputation", "Plan"]
    rows = []
    for a in agents:
        rows.append([
            a['agent_id'][:8],
            a['name'],
            a['role'],
            a['state'],
            f"{a['reputation']:.2f}",
            a['current_plan'] if a['current_plan'] else "-"
        ])
    
    print_table(headers, rows)

def cmd_feed(k):
    feed = k.introspection.get_social_feed(limit=20)
    print("\nSOCIAL FEED (Newest First)")
    print("=" * 60)
    
    if not feed:
        print("No posts.")
        return

    for p in feed:
        timestamp = p['timestamp'].split("T")[1][:8] if "T" in p['timestamp'] else p['timestamp']
        print(f"[{timestamp}] {p['agent_id'][:8]}: {p['content']}")
        if p['parent_id']:
            print(f"    -> Reply to {p['parent_id'][:8]}")
    print("=" * 60)

def cmd_decisions(k):
    decisions = k.introspection.get_decisions()
    print("\nDECISIONS")
    
    headers = ["ID", "Topic", "Status", "Result"]
    rows = []
    for d in decisions:
        rows.append([
            d['decision_id'][:8],
            d['topic'],
            d['status'],
            d['result'] if d['result'] else "-"
        ])
    
    print_table(headers, rows)

def cmd_plans(k):
    plans = k.introspection.get_plans()
    print("\nPLANS")
    
    if not plans:
        print("No active plans.")
        return

    for p in plans:
        print(f"\nPlan ID: {p['plan_id'][:8]} | Goal: {p['goal']} | Status: {p['status']}")
        print("-" * 50)
        
        headers = ["Step ID", "Status", "Description"]
        rows = []
        for s in p['steps']:
            rows.append([
                s['step_id'][:8],
                s['status'],
                s['description']
            ])
        print_table(headers, rows)

def main():
    parser = argparse.ArgumentParser(description="AI Ecosystem CLI")
    parser.add_argument("command", choices=["status", "agents", "feed", "decisions", "plans"], help="Command to execute")
    
    args = parser.parse_args()
    
    # Initialize Kernel in the background
    k = setup_demo_kernel()
    
    if args.command == "status":
        cmd_status(k)
    elif args.command == "agents":
        cmd_agents(k)
    elif args.command == "feed":
        cmd_feed(k)
    elif args.command == "decisions":
        cmd_decisions(k)
    elif args.command == "plans":
        cmd_plans(k)

if __name__ == "__main__":
    main()
