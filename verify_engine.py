import sys
import os
sys.path.append(os.getcwd())
try:
    from kernel.reputation import ReputationManager
    from kernel.decision_engine import DecisionEngine
    print("Imports successful")
    
    rep_mgr = ReputationManager()
    engine = DecisionEngine(rep_mgr)
    print("DecisionEngine initialized")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
