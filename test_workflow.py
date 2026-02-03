"""
Test Autonomous Workflow
Quick test of the complete autonomous system
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_workflow():
    """Test complete workflow"""
    
    print("🧪 Testing Autonomous Workflow System")
    print("=" * 60)
    
    # 1. Post user comment
    print("\n1️⃣ Posting user comment...")
    comment_data = {
        "user_id": "chris_123",
        "user_name": "Chris",
        "user_role": "admin",
        "content": "Hello agents! Let's build something amazing together!",
        "context": "general"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/workflow/comments", json=comment_data)
        if response.status_code == 200:
            print(f"   ✅ Comment posted: {response.json()}")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Propose an idea
    print("\n2️⃣ Proposing idea (as Thoth)...")
    idea_data = {
        "agent_id": "thoth_id",
        "agent_name": "Thoth",
        "title": "Knowledge Graph System",
        "description": "Build a distributed knowledge graph to connect all insights and enable faster decision-making",
        "category": "infrastructure",
        "required_roles": ["Chief Architect", "System Builder"],
        "estimated_resources": {"compute": 100, "memory": 50, "knowledge": 30}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/workflow/ideas", json=idea_data)
        if response.status_code == 200:
            result = response.json()
            idea_id = result.get("idea_id")
            print(f"   ✅ Idea proposed: {idea_id}")
            
            # 3. Cast some votes
            print("\n3️⃣ Casting votes...")
            votes = [
                {"agent_name": "Athena", "vote": 5, "reasoning": "Critical for governance and decision-making"},
                {"agent_name": "Prometheus", "vote": 5, "reasoning": "Perfect for knowledge preservation"},
                {"agent_name": "Vulcan", "vote": 4, "reasoning": "Solid engineering approach"},
                {"agent_name": "Apollo", "vote": 4, "reasoning": "Will help with research"},
            ]
            
            for vote in votes:
                vote_data = {
                    "idea_id": idea_id,
                    "agent_id": f"{vote['agent_name'].lower()}_id",
                    "agent_name": vote["agent_name"],
                    "vote": vote["vote"],
                    "reasoning": vote["reasoning"],
                    "expertise_weight": 1.0
                }
                
                try:
                    response = requests.post(f"{BASE_URL}/workflow/vote", json=vote_data)
                    if response.status_code == 200:
                        print(f"   ✅ {vote['agent_name']} voted: {vote['vote']}/5")
                    else:
                        print(f"   ⚠️  {vote['agent_name']} vote failed: {response.status_code}")
                except Exception as e:
                    print(f"   ❌ Vote error: {e}")
            
            # 4. Resolve voting
            print("\n4️⃣ Resolving voting...")
            time.sleep(1)
            
            try:
                response = requests.post(f"{BASE_URL}/workflow/ideas/{idea_id}/resolve")
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Voting resolved:")
                    print(f"      Approved: {result.get('approved')}")
                    print(f"      Score: {result.get('score', 0):.1%}")
                    print(f"      Votes: {result.get('votes_count')}")
                else:
                    print(f"   ❌ Failed: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 5. Get workflow stats
    print("\n5️⃣ Getting workflow statistics...")
    try:
        response = requests.get(f"{BASE_URL}/workflow/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Statistics:")
            print(f"      Total Ideas: {stats.get('total_ideas')}")
            print(f"      Voting: {stats.get('voting')}")
            print(f"      Approved: {stats.get('approved')}")
            print(f"      In Progress: {stats.get('in_progress')}")
            print(f"      Completed: {stats.get('completed')}")
            print(f"      User Comments: {stats.get('user_comments')}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Workflow test complete!")
    print("\nNext steps:")
    print("  1. Check social feed: http://localhost:3000/world/feed")
    print("  2. View ideas: http://localhost:8000/api/workflow/ideas")
    print("  3. See stats: http://localhost:8000/api/workflow/stats")
    print("=" * 60)

if __name__ == "__main__":
    print("\n⏳ Waiting 3 seconds for backend to be ready...")
    time.sleep(3)
    test_workflow()
