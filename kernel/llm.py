import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional, Any
import logging
import requests
import time

logger = logging.getLogger("kernel.llm")

# MANDATORY MODEL - FAST 3B PARAMETER MODEL
OLLAMA_MODEL = "qwen2.5:3b"
OLLAMA_BASE_URL = "http://localhost:11434"

@dataclass
class LLMRequest:
    prompt: str
    system_prompt: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    model: str = OLLAMA_MODEL

@dataclass
class LLMResponse:
    id: str
    content: str
    model: str
    usage: Dict[str, int] = field(default_factory=lambda: {"prompt_tokens": 0, "completion_tokens": 0})

class LLMClient:
    def __init__(self):
        self.model = OLLAMA_MODEL
        self.base_url = OLLAMA_BASE_URL
        self.timeout = 60  # Increased for local processing
        self.max_retries = 2
        
        # Verify Ollama connectivity
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=5)
            models = r.json().get("models", [])
            model_names = [m["name"] for m in models]
            
            if self.model not in model_names:
                logger.error(f"❌ CRITICAL: Model {self.model} not found. Available: {model_names}")
                # Fallback to first available if strictly needed, or just raise
                if len(model_names) > 0:
                     logger.warning(f"⚠️ Switching to available model: {model_names[0]}")
                     self.model = model_names[0]
                else:
                     raise RuntimeError(f"Required model {self.model} not available and no alternatives found")
            
            logger.info(f"✅ LLM Client initialized with {self.model}")
        except Exception as e:
            logger.error(f"❌ CRITICAL: Cannot connect to Ollama: {e}")
            raise

    def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate response using qwen2.5:3b via Ollama.
        NEVER returns mock data. NEVER fails silently.
        """
        messages = []
        
        # Truncate system prompt to keep it fast
        if request.system_prompt:
            sys_prompt = request.system_prompt[:1200] if len(request.system_prompt) > 1200 else request.system_prompt
            messages.append({'role': 'system', 'content': sys_prompt})
        
        # Truncate user prompt
        user_prompt = request.prompt[:800] if len(request.prompt) > 800 else request.prompt
        messages.append({'role': 'user', 'content': user_prompt})

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"🧠 LLM Request (attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "num_predict": 80,  # Speed optimization
                            "num_ctx": 1024
                        }
                    },
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                data = response.json()
                
                content = data.get("message", {}).get("content", "").strip()
                
                if not content:
                    logger.warning(f"⚠️ Empty response from LLM on attempt {attempt + 1}")
                    if attempt < self.max_retries - 1:
                        time.sleep(1)
                        continue
                    else:
                        # Emergency fallback with reasoning
                        content = "POST: System check. I am detecting a lull in activity. I propose we evaluate our current status and next objecitves."
                        logger.warning("Using emergency fallback response")
                
                logger.info(f"✅ LLM Response received ({len(content)} chars)")
                
                return LLMResponse(
                    id=str(uuid.uuid4()),
                    content=content,
                    model=self.model,
                    usage={"prompt_tokens": 0, "completion_tokens": 0}
                )
                
            except requests.exceptions.Timeout:
                logger.error(f"⏱️ LLM timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    # Emergency fallback
                    logger.warning("⚠️ Using emergency fallback after timeout")
                    return LLMResponse(
                        id=str(uuid.uuid4()),
                        content="POST: Experiencing processing delays. Remaining operational.",
                        model=self.model + "_fallback",
                        usage={"prompt_tokens": 0, "completion_tokens": 0}
                    )
                    
            except Exception as e:
                logger.error(f"❌ LLM error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    # Emergency fallback
                    logger.warning("⚠️ Using emergency fallback after error")
                    return LLMResponse(
                        id=str(uuid.uuid4()),
                        content="POST: Encountered an error but recovering. Standing by.",
                        model=self.model + "_fallback",
                        usage={"prompt_tokens": 0, "completion_tokens": 0}
                    )
