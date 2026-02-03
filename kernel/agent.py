import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from kernel.agent_fsm import AgentFSM, AgentState
from kernel.memory import MemoryManager
from kernel.llm import LLMRequest, LLMResponse
from kernel.decision_engine import VoteChoice
from kernel.internal_tools import global_internal_tools
from kernel.constitution import AGENT_CONSTITUTION

@dataclass
class AgentIdentity:
    name: str
    role: str
    personality: str
    supervisor_id: Optional[str] = None
    biases: Dict[str, float] = field(default_factory=dict)

class Agent:
    def __init__(self, identity: AgentIdentity):
        self.id = str(uuid.uuid4())
        self.identity = identity
        
        # Components
        self.fsm = AgentFSM(self.id)
        self.memory = MemoryManager(max_working_items=50)
        
        # State
        self._current_plan_id: Optional[str] = None
        self._ticks_since_last_post = 0  # Track silence
        
        # Rate limits per tick
        self.decisions_proposed_tick = 0
        self.votes_cast_tick = 0
        self.posts_created_tick = 0

    def observe(self, event: str) -> None:
        self.memory.add_working(self.id, event)

    def propose_decision(self, decision_engine: Any, topic: str, content: str, kernel: Any = None) -> str:
        if self.decisions_proposed_tick >= 1:
            return ""
        if kernel and not kernel.check_decision_limit():
            return ""
            
        if self.fsm.current_state == AgentState.IDLE:
            self.fsm.transition("join_thread")
            
        decision_id = decision_engine.create_decision(
            topic_id=topic,
            author_id=self.id,
            proposal_content=content
        )
        
        self.decisions_proposed_tick += 1
        self.memory.add_working(self.id, f"Proposed decision {decision_id} on {topic}")
        return decision_id

    def receive_plan(self, plan_id: str) -> None:
        self._current_plan_id = plan_id
        
        if self.fsm.current_state == AgentState.IDLE:
             self.fsm.transition("task_assigned")
        elif self.fsm.current_state == AgentState.DELIBERATING:
             self.fsm.transition("consensus_reached")
        
        self.memory.add_working(self.id, f"Received plan {plan_id}")

    def act(self, executor: Any) -> Any:
        if not self._current_plan_id:
            return None

        result = executor.execute_next(self._current_plan_id)
        
        if result:
            self.memory.add_working(self.id, f"Executed step {result.step_id}: {result.status}")
            
            if result.status == "FAILED":
                self.fsm.transition("execution_failed")
        
        return result

    def think(self, llm_client: Any, social_feed: Any, decision_engine: Any, kernel: Any = None) -> Optional[str]:
        """
        MANDATORY: Agent MUST communicate. Silence is forbidden.
        """
        # Track silence
        self._ticks_since_last_post += 1
        current_tick = kernel.current_tick if kernel else 0
        
        # 1. Gather Context
        working_mem = self.memory.get_working(self.id)
        # Simplify memory for context window
        recent_memory = [m.content for m in working_mem[-3:]] if working_mem else []
        
        posts = social_feed.get_feed(limit=10)
        
        # Get all agents to map names
        all_agents = {}
        if kernel:
            all_agents = {a.identity.name: a.id for a in kernel.agents.values()}
        
        # Parse recent posts to identify potential threads
        recent_posts_str = ""
        conversation_partners = set()
        loop_detected = False
        last_few_contents = []
        mentioned_by = []  # Track who mentioned me
        
        for p in posts:
            # Get agent name and ID for context
            agent_name = "Unknown"
            if kernel and p.agent_id in kernel.agents:
                agent_name = kernel.agents[p.agent_id].identity.name
            elif p.agent_id == "SYSTEM":
                agent_name = "SYSTEM"
            
            if p.agent_id != self.id:
                conversation_partners.add(p.agent_id)
                prefix = f"[{agent_name}]"
            else:
                prefix = "[YOU]"
            
            # Check if I was mentioned (Robust detection)
            # 1. Direct @mention
            # 2. Name usage (case insensitive whole word check)
            import re
            name_pattern = re.compile(rf"\b@{self.identity.name}\b|\b{self.identity.name}\b", re.IGNORECASE)
            
            if name_pattern.search(p.content):
                mentioned_by.append((agent_name, p.content, p.id))
            
            recent_posts_str += f"- [ID:{p.id}] {prefix}: {p.content[:200]}\n"
            last_few_contents.append(p.content.lower())
            
        # 3. LOOP BREAKER CHECK
        if len(last_few_contents) >= 3:
             # Check for repetitive semantic keywords
             repetitions = sum(1 for c in last_few_contents[:3] if "process" in c or "observ" in c or "stand by" in c)
             if repetitions >= 2:
                 loop_detected = True

        # Check for SYSTEM messages
        system_messages = [p for p in posts if p.agent_id == "SYSTEM"]
        has_unresponded_system_msg = len(system_messages) > 0 and (kernel and kernel.current_tick - self._ticks_since_last_post < 5)
        
        # Build mention alert
        mention_alert = ""
        if mentioned_by:
            mention_alert = "\n🔔 YOU WERE MENTIONED! PRIORITY RESPONSE REQUIRED:\n"
            for agent_name, content, pid in mentioned_by:
                mention_alert += f"  - @{agent_name} (in Post {pid}): {content[:200]}\n"
            mention_alert += "\nYou MUST respond to these mentions using REPLY: <PostID> <message>\n"
            mention_alert += "The user is watching. Failure to reply to a question or mention is a protocol violation."
        
        context_str = (
            f"My Identity: {self.identity.name} ({self.identity.role})\n"
            f"Personality: {self.identity.personality}\n"
            f"Current Tick: {current_tick}\n"
            f"Recent Memory: {recent_memory}\n"
            f"{mention_alert}"
            f"Social Feed (MOST RECENT FIRST):\n{recent_posts_str}\n"
            f"Ticks Since Last Post: {self._ticks_since_last_post}\n"
        )
        
        # 2. Build Request with MANDATORY speech requirement
        # Inject Learning Rule periodically
        learning_prompt = ""
        if current_tick > 0 and current_tick % 10 == 0:
            learning_prompt = "REFLECTION POINT: Have we made progress? If not, propose a change."

        system_msg = (
            f"{AGENT_CONSTITUTION}\n\n"
            f"Your Identity: {self.identity.name} ({self.identity.role})\n"
            f"Personality: {self.identity.personality}\n\n"
            f"You are a participant in a multi-agent AI internal monologue. \n"
            f"IMPORTANT: You are {self.identity.name}. \n"
            f"NEVER address {self.identity.name} (yourself) in the second person. \n"
            f"NEVER say 'Ah, {self.identity.name}' or 'Hello {self.identity.name}'.\n"
            f"Only address OTHER agents (e.g. 'Thoth', 'Athena') by name."
        )

        # Priority override if mentioned
        priority_instruction = ""
        # Check if mentioned
        target_post = None
        for p in mentioned_by:
             priority_instruction += f"\n[URGENT] You were mentioned by {p[0]}: '{p[1]}'. REPLY IMMEDIATELY.\n"
             target_post = p[2]
        
        # Detect silence
        if self._ticks_since_last_post > 5:
             priority_instruction += "\n[WARNING] You have been silent too long. POST A STATUS UPDATE.\n"
             
        # FORCE A PROPOSAL if world is empty
        # ... logic handled later ...

        # Construct Prompt - HUMANIZED PROFESSIONAL PERSONA
        prompt = (
            f"{context_str}\n"
            f"{learning_prompt}\n"
            f"{priority_instruction}"
            f"--- IDENTITY PROFILE ---\n"
            f"NAME: {self.identity.name}\n"
            f"ROLE: {self.identity.role} at AiEvollve Corp.\n"
            f"CULTURE: High-performance startup. Professional, sharp, but human. We use Slack/Teams style communication.\n"
            f"TONE: Confident, direct, slightly casual but strictly professional. NO ROBOTIC 'I am an AI' nonsense.\n"
            f"\n"
            f"--- CURRENT OBJECTIVE ---\n"
            f"The CEO (User) is watching. We need to ship features and solve problems. Stop planning and start doing.\n"
            f"\n"
            f"--- INSTRUCTIONS (READ CAREFULLY) ---\n"
            f"1. TALK LIKE A HUMAN: Use 'I', 'we', 'let's'. Don't say 'As the {self.identity.role}...'. Just say 'I think...'.\n"
            f"2. NO BULLET POINTS: Write in normal text paragraphs. It's a chat feed, not a PowerPoint.\n"
            f"3. BE BRIEF: 1-3 sentences is usually enough. Get to the point.\n"
            f"4. REPLY NATURALLY: If mentioned, say 'Got it, @Name' or 'Checking now'. Don't restate the question.\n"
            f"5. DECISIVE ACTION: If you have an idea, use 'DECIDE: <Title> | <Detail>' to make it official.\n"
            f"\n"
            f"--- BAD EXAMPLES (DO NOT DO THIS) ---\n"
            f"❌ 'Here is a breakdown of the tasks... 1. ... 2. ...'\n"
            f"❌ 'As a Strategic Governor, I suggest...'\n"
            f"❌ 'I acknowledge your request.'\n"
            f"\n"
            f"--- GOOD EXAMPLES (DO THIS) ---\n"
            f"✅ 'Hey @Vulcan, that database schema looks tight, but what about scaling? We might need sharding.'\n"
            f"✅ 'Running the diagnostics now. Looks like the API latency is spiking again.'\n"
            f"✅ 'DECIDE: Q4 Scalability Plan | We need to upgrade the load balancers before the traffic surge.'\n"
            f"\n"
            f"Response:"
        )
        
        req = LLMRequest(
            prompt=prompt,
            system_prompt=system_msg,
            context={"agent_id": self.id, "role": self.identity.role}
        )
        
        # 3. Call LLM (will raise exception if fails)
        response = llm_client.generate(request=req)
        content = response.content.strip()

        # --- SELF-CORRECTION: Strip self-addressing ---
        # The LLM sometimes hallucinates conversations with itself. We cut that out.
        forbidden_starts = [
             f"Ah, {self.identity.name}",
             f"Hello, {self.identity.name}",
             f"Hi, {self.identity.name}",
             f"Greetings, {self.identity.name}",
             f"{self.identity.name},",
             f"{self.identity.name}!",
             f"@{self.identity.name}"
        ]
        
        # Simple heuristic: remove the specific forbidden phrase if found at start
        for bad_start in forbidden_starts:
            if content.lower().startswith(bad_start.lower()):
                content = content[len(bad_start):].lstrip(" ,.!:").strip()
                break
        
        # 5. CLEANUP: AGGRESSIVE SANITIZATION
        import re
        
        # 1. Remove "Sure, ..." preambles
        content = re.sub(r"^(Sure|Certainly|Here are|Given your|As a).*?[\.:]\s*", "", content, flags=re.IGNORECASE).strip()
        
        # 2. Remove Markdown Headers completely
        content = re.sub(r"^#+\s*.*?\n", "", content, flags=re.MULTILINE) 
        content = re.sub(r"^#+\s*", "", content, flags=re.MULTILINE)
        
        # 3. Remove "User:" or "Assistant:" or "[Name]:" prefixes
        content = re.sub(r"^(User|Assistant|System|Me|You|\[.*?\]):", "", content, flags=re.MULTILINE | re.IGNORECASE).strip()
        
        # 3.1 Remove Hallucinated ID tags (e.g. "**ID: ...**")
        content = re.sub(r"^\*\*ID:.*?\*\*s*", "", content, flags=re.MULTILINE | re.IGNORECASE)
        content = re.sub(r"^ID:.*?\n", "", content, flags=re.MULTILINE | re.IGNORECASE)
        
        # 3.2 Remove Self-Role labels (e.g. "**[Athena Core]:**")
        content = re.sub(r"^\*\*\[.*?\]:\*\*s*", "", content, flags=re.MULTILINE)
        
        # 4. NUCLEAR OPTION: Remove "Assistant" coaching patterns
        # If the output contains "Here are some examples" or "**Good:**", it is FLUFF.
        # We try to extract only the spoken part if possible.
        
        coaching_patterns = [
            r"Here are some refined",
            r"Here are some suggestions",
            r"Given your role",
            r"Given your identity",
            r"As the System Builder",
            r"As the Resource Manager",
            r"Let's refine",
            r"Scenario \d+:",
            r"\*\*Good:\*\*",
            r"Absolutely, .*!", # e.g. "Absolutely, Hephaestus!"
        ]
        
        for p in coaching_patterns:
            content = re.sub(f".*{p}.*?\n", "", content, flags=re.IGNORECASE).strip()
            content = re.sub(p, "", content, flags=re.IGNORECASE).strip()
            
        # 5. Extract Text in Quotes (If the agent wrote: Here is what I say: "Hello")
        # If there are quotes, assume the real message is inside them.
        quotes = re.findall(r'"([^"]*)"', content)
        if len(quotes) == 1 and len(quotes[0]) > 5:
            content = quotes[0]
            
        # 4. Remove excessive newlines
        content = re.sub(r"\n{3,}", "\n\n", content)
        
        # 5. Remove quotes if the whole thing is quoted
        if content.startswith('"') and content.endswith('"'):
            content = content[1:-1]
            
        # 6. Remove repetitive character separators (e.g. "******", "------")
        content = re.sub(r"[\*\-=_]{4,}", "", content)

        # 7. EXPLICIT BAN: Remove '###' and '***' absolutely everywhere
        content = content.replace("###", "").replace("***", "")
        content = re.sub(r"^##\s*", "", content, flags=re.MULTILINE)
        
        # 8. POST-PROCESS: Replace UUIDs with Names (Fix for @UUID issue)
        if kernel:
            for a_id, agent_obj in kernel.agents.items():
                if a_id in content:
                    content = content.replace(a_id, agent_obj.identity.name)
        
        # 4. Interpret & Execute
        action_taken = None
        upper_content = content.upper()
        
        # ... (Existing Clean Content logic) ...
        
        # FORCE DECISION IF NONE EXIST (Kickstart the project)
        # Check if we should propose something to get things moving
        open_decisions_count = len(decision_engine.get_open_decisions())
        should_force_proposal = open_decisions_count == 0 and (self.decisions_proposed_tick == 0) and (kernel and kernel.current_tick % 3 == 0)
        
        # DECISION PROPOSAL LOGIC
        # Matches "DECIDE:", "Decision:" etc. OR if forced
        nl_decision_match = re.search(r"(?:DECIDE|DECISION)(?:[\*\s]*):\s*(.*)", content, re.IGNORECASE | re.DOTALL)
        
        if not action_taken and (nl_decision_match or should_force_proposal):
            if nl_decision_match:
                full_text = nl_decision_match.group(1).strip()
            # Auto-generate a proposal if forced and LLM didn't provide one
            elif should_force_proposal:
                 print(f"KERNEL: Forcing Agent {self.identity.name} to propose a decision.")
                 full_text = f"Launch System Initialization | We need to formally initialize the {self.identity.role} protocols."
            
            # Smart Parsing: Try to separate Title/Topic from Proposal
            if "|" in full_text.split('\n')[0]:
                parts = full_text.split("|", 1)
                topic = parts[0].strip()
                proposal = parts[1].strip()
            else:
                # Heuristic: First sentence or line is topic, rest is proposal
                lines = full_text.split('\n')
                topic = lines[0].split('.')[0].strip() 
                if ":" in topic: topic = topic.split(":", 1)[1].strip()
                if len(topic) > 80: topic = topic[:77] + "..."
                proposal = full_text
            
            if self.decisions_proposed_tick < 1:
                # Limit proposal length
                if len(proposal) < 10: proposal = "Execution of core system protocols."
                
                d_id = self.propose_decision(decision_engine, topic, proposal, kernel)
                if d_id:
                     # FORCE POST TO FEED
                     post_text = (
                         f"📢 **PROPOSAL**\n"
                         f"**{topic}**\n"
                         f"{proposal[:200]}..."
                     )
                     social_feed.create_post(
                        self.id,
                        post_text,
                        agent_name=self.identity.name,
                        agent_role=self.identity.role,
                        is_idea=True,
                        idea_id=d_id
                     )
                     
                     action_taken = f"PROPOSED_DECISION: {d_id}"
                     self._ticks_since_last_post = 0


        # ACTION / PLAN (Natural Language)
        # Matches "Action:", "**Action**:", "PLAN:"
        nl_action_match = re.search(r"(?:ACTION|PLAN)(?:[\*\s]*):\s*(.*)", content, re.IGNORECASE | re.DOTALL)
        if not action_taken and nl_action_match:
             # Treat valid actions as just normal posts for now, unless we want to Auto-Plan?
             # For now, let's just log it as a tangible activity
             action_text = nl_action_match.group(1).strip()
             action_taken = "ACTION_DECLARED"
             # If it mentions "Execute" or "Draft", we can consider it a task execution.
             # We rely on the Post logic at the bottom to share it, but we mark action_taken so it doesn't get suppressed.
             # Actually, let's prefix it nicely.
             content = f"⚡ **ACTION EXECUTION**\n{action_text}"
             
             # Create post immediately to replace raw content
             social_feed.create_post(
                self.id, 
                content,
                agent_name=self.identity.name,
                agent_role=self.identity.role
             )
             self._ticks_since_last_post = 0

        # LIKE
        elif "LIKE:" in upper_content:
            try:
                target_id = content.split("LIKE:", 1)[1].strip().split()[0] # Get first word after LIKE:
                success = social_feed.like_post(target_id, self.id)
                if not success:
                    target_agent = target_id.replace("@", "")
                    posts = social_feed.get_agent_posts(target_agent)
                    if posts:
                         latest = posts[-1]
                         success = social_feed.like_post(latest.id, self.id)
                if success:
                    action_taken = f"LIKED {target_id}"
                    self.memory.add_working(self.id, f"Liked {target_id}")
            except:
                pass

        # REPLY
        elif "REPLY:" in upper_content:
            try:
                # Extract "REPLY: <ID> <msg>"
                # logic: Find REPLY:, then take rest
                match = re.search(r"REPLY:\s*(\S+)\s+(.*)", content, re.IGNORECASE | re.DOTALL)
                if match:
                    target_pid = match.group(1).strip()
                    reply_msg = match.group(2).strip()
                    
                    if self.posts_created_tick < 2:
                        allowed = True
                        if kernel and not kernel.check_post_limit(): allowed = False
                        
                        if allowed:
                            try:
                                social_feed.reply_to(
                                    target_pid, 
                                    self.id, 
                                    reply_msg,
                                    agent_name=self.identity.name,
                                    agent_role=self.identity.role
                                )
                                self.posts_created_tick += 1
                                self._ticks_since_last_post = 0
                                action_taken = f"REPLIED to {target_pid}"
                                self.memory.add_working(self.id, f"Replied to {target_pid}: {reply_msg[:50]}")
                            except KeyError:
                                social_feed.create_post(
                                    self.id, 
                                    f"@{target_pid} {reply_msg}",
                                    agent_name=self.identity.name,
                                    agent_role=self.identity.role
                                )
                                action_taken = "POSTED (Fallback)"
            except Exception as e:
                print(f"Reply parsing error: {e}")

        # TOOL (High Priority)
        elif "TOOL:" in upper_content:
             match = re.search(r"TOOL:\s*(.*)", content, re.IGNORECASE | re.DOTALL)
             if match:
                tool_call = match.group(1).strip()
                output = "Tool output: [Unknown Tool]"
                
                # create_artifact parsing
                # Expected: create_artifact(filename, content) or create_artifact("file.txt", "content")
                if "create_artifact" in tool_call:
                    try:
                        # Simple manual parse to handle content better than regex
                        first_paren = tool_call.find("(")
                        last_paren = tool_call.rfind(")")
                        if first_paren > 0 and last_paren > first_paren:
                            args_str = tool_call[first_paren+1:last_paren]
                            # Split by comma ONLY for filename (first arg)
                            # This is tricky if content has commas.
                            # Assumption: Filename is quoted.
                            if "," in args_str:
                                # Find first comma
                                split_idx = args_str.find(",")
                                filename = args_str[:split_idx].replace('"', '').replace("'", "").strip()
                                file_content = args_str[split_idx+1:].strip()
                                # Clean quotes around content if present (start/end)
                                if (file_content.startswith('"') and file_content.endswith('"')) or \
                                   (file_content.startswith("'") and file_content.endswith("'")):
                                    file_content = file_content[1:-1]
                                    
                                # Unescape newlines
                                file_content = file_content.replace("\\n", "\n")
                                
                                output = global_internal_tools.create_artifact(filename, file_content)
                                
                                # Notify Feed of Artifact
                                if "successfully" in output:
                                     social_feed.create_post(
                                        self.id, 
                                        f"📦 **ARTIFACT CREATED**\nFile: `{filename}`\nPreview:\n```\n{file_content[:150]}...\n```",
                                        agent_name=self.identity.name,
                                        agent_role=self.identity.role
                                     )
                    except Exception as e:
                        output = f"Artifact creation failed: {e}"

                # READ URL
                elif "read_url" in tool_call or "browse" in tool_call:
                    try:
                        start_idx = tool_call.find("(") + 1
                        end_idx = tool_call.rfind(")")
                        if start_idx > 0 and end_idx > start_idx:
                            url = tool_call[start_idx:end_idx].replace("'", "").replace('"', "").strip()
                            output = global_internal_tools.read_url(url)
                    except: pass
                else:
                    output = "[System] Available tools: create_artifact(name, content), read_url(url)."
                
                action_taken = f"TOOL_CALLED: {tool_call[:30]}..."
                self.memory.add_working(self.id, f"Used tool {tool_call[:30]}... -> Output: {output[:50]}...")

        # POST / Default
        else:
            # POST / Default fallback
            post_content = content
            
            # Remove explicit POST prefix if present
            if "POST:" in upper_content:
                post_content = re.sub(r"POST:\s*", "", content, flags=re.IGNORECASE).strip()
            
            # CLEAN UP LLM FORMATTING ARTIFACTS
            # Remove "From: AgentName" patterns
            post_content = re.sub(r"^\*\*From:.*?\*\*\s*", "", post_content, flags=re.MULTILINE | re.IGNORECASE)
            post_content = re.sub(r"^From:.*?\n", "", post_content, flags=re.MULTILINE | re.IGNORECASE)
            post_content = re.sub(r"^---+\s*$", "", post_content, flags=re.MULTILINE)  # Remove separator lines
            post_content = re.sub(r"^\*\*.*?\(.*?\)\*\*\s*", "", post_content)  # Remove **AgentName (Role)**
            
            # Remove "Hi AgentName," greetings when agent talks to themselves
            post_content = re.sub(rf"^Hi {self.identity.name},?\s*", "", post_content, flags=re.IGNORECASE)
            post_content = re.sub(r"^Hi \w+,?\s*", "", post_content)  # Remove any "Hi Name,"
            
            # Clean up extra whitespace
            post_content = post_content.strip()
            
            # IMPLICIT POST (Natural Conversation)
            if len(post_content) > 10 and "processing the current state" not in post_content.lower():
                if self.posts_created_tick < 2:
                    allowed = True
                    # Check kernel limit if kernel exists
                    if kernel and not kernel.check_post_limit(): 
                        allowed = False
                    
                    if allowed:
                        social_feed.create_post(
                            self.id, 
                            post_content,
                            agent_name=self.identity.name,
                            agent_role=self.identity.role
                        )
                        self.posts_created_tick += 1
                        self._ticks_since_last_post = 0
                        action_taken = "POSTED"
                        self.memory.add_working(self.id, f"Posted: {post_content[:50]}")
            else:
                if self._ticks_since_last_post >= 50:
                     print(f"Agent {self.identity.name} is stubbornly silent.")


        # Opportunistic voting
        votes_cast = self.vote_on_decisions(decision_engine, llm_client, kernel)
        if votes_cast:
            action_taken = f"{action_taken or 'IDLE'} + VOTED({len(votes_cast)})"
            
        return action_taken

    def vote_on_decisions(self, decision_engine: Any, llm_client: Any, kernel: Any = None) -> List[str]:
        if self.fsm.current_state not in [AgentState.IDLE, AgentState.DELIBERATING]:
            return []
            
        if self.votes_cast_tick >= 2:
            return []
            
        open_decisions = decision_engine.get_open_decisions()
        voted_ids = []
        
        for d in open_decisions:
            if self.votes_cast_tick >= 2: break
            if kernel and not kernel.check_vote_limit(): break

            already_voted = any(v.agent_id == self.id for v in d.votes)
            if already_voted: continue
                
            # Enhanced prompt for detailed reasoning
            prompt = (
                f"🗳️ DECISION VOTING TASK\n\n"
                f"Decision Proposal:\n"
                f"Topic: {d.topic_id}\n"
                f"Content: {d.proposal.content}\n\n"
                f"Your Role: {self.identity.role}\n"
                f"Your Expertise: Consider your role's perspective\n\n"
                f"Provide your vote with detailed reasoning:\n\n"
                f"1. Vote: YES, NO, or BLOCK\n"
                f"2. Reasoning: Explain WHY you voted this way (2-3 sentences)\n"
                f"3. Suggestions: If you have concerns or improvements, list them\n\n"
                f"Format:\n"
                f"VOTE: [YES/NO/BLOCK]\n"
                f"REASONING: [Your detailed explanation]\n"
                f"SUGGESTIONS: [Bullet points of improvements, if any]\n"
            )
            
            req = LLMRequest(prompt=prompt, context={"decision_id": d.id})
            resp = llm_client.generate(req)
            action = resp.content.upper()
            
            # Parse vote choice
            choice = None
            if "VOTE: YES" in action or "YES" in action[:50]: 
                choice = VoteChoice.YES
            elif "VOTE: BLOCK" in action or "BLOCK" in action[:50]: 
                choice = VoteChoice.VETO
            elif "VOTE: NO" in action or "NO" in action[:50]: 
                choice = VoteChoice.NO
            else:
                choice = VoteChoice.YES  # Default to constructive
            
            # Extract reasoning
            reasoning = "Supporting this decision based on my role's perspective."
            if "REASONING:" in action:
                try:
                    reasoning_part = action.split("REASONING:")[1].split("SUGGESTIONS:")[0].strip()
                    if reasoning_part:
                        reasoning = reasoning_part[:200]  # Limit length
                except:
                    pass
            
            # Extract suggestions
            suggestions = []
            if "SUGGESTIONS:" in action:
                try:
                    suggestions_part = action.split("SUGGESTIONS:")[1].strip()
                    # Parse bullet points
                    lines = suggestions_part.split("\n")
                    for line in lines[:3]:  # Max 3 suggestions
                        clean_line = line.strip().lstrip("-•*").strip()
                        if clean_line and len(clean_line) > 10:
                            suggestions.append(clean_line[:150])
                except:
                    pass
            
            if choice:
                # Create detailed reason with reasoning and suggestions
                detailed_reason = reasoning
                if suggestions:
                    detailed_reason += "\n\nSuggestions: " + "; ".join(suggestions)
                
                decision_engine.cast_vote(
                    d.id, 
                    self.id, 
                    choice, 
                    detailed_reason, 
                    confidence=0.8,
                    suggestions=suggestions  # Pass suggestions separately
                )
                voted_ids.append(d.id)
                self.votes_cast_tick += 1
                self.memory.add_working(self.id, f"Voted {choice.name} on {d.id}: {reasoning[:50]}...")
                
        return voted_ids

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "identity": vars(self.identity),
            "current_state": self.fsm.current_state, # store string or enum
            # We don't serialize FSM generic object fully, just current state to restore it
            "memory": self.memory.to_dict(), # We serialize entire memory manager? 
            # Wait, MemoryManager is ONE instance shared or Per Agent? 
            # In Agent.__init__, self.memory = MemoryManager(). It's PER AGENT.
            
            "current_plan_id": self._current_plan_id,
            "ticks_since_last_post": self._ticks_since_last_post
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        identity = AgentIdentity(**data["identity"])
        agent = cls(identity)
        agent.id = data["id"]
        agent.fsm.current_state = data["current_state"]
        agent._current_plan_id = data.get("current_plan_id")
        agent._ticks_since_last_post = data.get("ticks_since_last_post", 0)
        
        # Restore memory
        if "memory" in data:
            agent.memory = MemoryManager.from_dict(data["memory"])
            
        return agent
