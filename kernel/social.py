import uuid
import datetime
from typing import List, Dict, Optional, Any
# Import the enhanced system
from kernel.enhanced_social import global_enhanced_feed

# We keep the Post abstraction but now it's just an alias or wrapper if needed.
# Actually, let's just use the Enhanced Post object directly as it's compatible enough.
from kernel.enhanced_social import Post

class SocialFeed:
    """
    Legacy wrapper around EnhancedSocialFeed to maintain compatibility
    while switching to the new X-style backend.
    """
    def __init__(self):
        # We don't maintain local state anymore; we use the global enhanced feed
        pass

    def create_post(self, agent_id: str, content: str, parent_id: Optional[str] = None, agent_name: str = "Unknown", agent_role: str = "Assistant", is_idea: bool = False, idea_id: Optional[str] = None) -> str:
        """
        Creates a new post (root or reply).
        Now accepts agent_name and agent_role for better UI.
        Also accepts is_idea and idea_id for Decision/Idea tracking.
        """
        return global_enhanced_feed.create_post(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_role=agent_role,
            content=content,
            parent_id=parent_id,
            is_idea=is_idea,
            idea_id=idea_id
        )

    def reply_to(self, post_id: str, agent_id: str, content: str, agent_name: str = "Unknown", agent_role: str = "Assistant") -> str:
        """
        Creates a reply to an existing post.
        """
        result = global_enhanced_feed.reply_to_post(
            post_id=post_id,
            agent_id=agent_id,
            agent_name=agent_name,
            agent_role=agent_role,
            content=content
        )
        if result:
            return result
        else:
            # Fallback if parent not found, create new post
            return self.create_post(agent_id, f"@{post_id} {content}", agent_name=agent_name, agent_role=agent_role)
    
    def like_post(self, post_id: str, agent_id: str) -> bool:
        """
        Records a like from an agent.
        """
        return global_enhanced_feed.like_post(post_id, agent_id)

    def get_feed(self, limit: int = 50) -> List[Post]:
        """
        Returns the most recent posts globally.
        """
        # Map get_feed to get_timeline
        return global_enhanced_feed.get_timeline(limit=limit, include_replies=True)

    def get_thread(self, post_id: str) -> List[Post]:
        """
        Returns flatted thread.
        """
        return global_enhanced_feed.get_thread(post_id)

    def get_agent_posts(self, agent_id: str) -> List[Post]:
        """
        Returns all posts by a specific agent.
        """
        return global_enhanced_feed.get_agent_posts(agent_id)

    def to_dict(self) -> Dict[str, Any]:
        return global_enhanced_feed.to_dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SocialFeed':
        # EnhancedFeed handles its own state, nothing to restore here locally
        # Ideally we load state into global_enhanced_feed if we built persistence for it.
        # For now, we return a new instance which points to the global singleton.
        return cls()

