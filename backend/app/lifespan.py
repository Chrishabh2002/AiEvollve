from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.app.state import global_state
from backend.app.tick import run_simulation_loop
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Initializing AI World Kernel...")
    global_state.initialize_kernel()
    
    # Start simulation loop automatically
    global_state.is_running = True
    loop = asyncio.get_event_loop()
    global_state.simulation_task = loop.create_task(run_simulation_loop())
    print("Simulation loop started automatically.")
    
    yield
    
    # Shutdown
    print("Shutting down AI World Kernel...")
    global_state.is_running = False
    if global_state.simulation_task:
        global_state.simulation_task.cancel()
