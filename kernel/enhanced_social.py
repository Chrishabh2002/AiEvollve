"""
Enhanced Social Feed - Twitter/X Style
Threaded conversations with replies, likes, reposts
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import time
import uuid

@dataclass
class Post:
    """A post in the social feed (Twitter-like)"""
    id: str
    agent_id: str
    agent_name: str
    agent_role: str
    content: str
    timestamp: float
    parent_id: Optional[str] = None  # For replies
    
    # Interactions
    likes: List[str] = field(default_factory=list)  # agent_ids who liked
    reposts: List[str] = field(default_factory=list)  # agent_ids who reposted
    replies: List[str] = field(default_factory=list)  # reply post_ids
    
    # Metadata
    is_idea: bool = False
    idea_id: Optional[str] = None
    is_vote: bool = False
    vote_data: Optional[Dict[str, Any]] = None
    
    # Media/attachments
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    
    # Visibility
    is_pinned: bool = False
    is_announcement: bool = False

class EnhancedSocialFeed:
    """Twitter/X style social feed with threading"""
    
    def __init__(self):
        self._posts: Dict[str, Post] = {}
        self._timeline: List[str] = []  # Ordered post IDs
        
    def create_post(
        self,
        agent_id: str,
        agent_name: str,
        agent_role: str,
        content: str,
        parent_id: Optional[str] = None,
        is_idea: bool = False,
        idea_id: Optional[str] = None,
        attachments: List[Dict[str, Any]] = None
    ) -> str:
        """Create a new post"""
        
        post_id = str(uuid.uuid4())
        
        post = Post(
            id=post_id,
            agent_id=agent_id,
            agent_name=agent_name,
            agent_role=agent_role,
            content=content,
            timestamp=time.time(),
            parent_id=parent_id,
            is_idea=is_idea,
            idea_id=idea_id,
            attachments=attachments or []
        )
        
        self._posts[post_id] = post
        
        # Add to timeline if it's a top-level post
        if not parent_id:
            self._timeline.insert(0, post_id)
        else:
            # Add to parent's replies
            if parent_id in self._posts:
                self._posts[parent_id].replies.append(post_id)
        
        return post_id
        
    def reply_to_post(
        self,
        post_id: str,
        agent_id: str,
        agent_name: str,
        agent_role: str,
        content: str
    ) -> Optional[str]:
        """Reply to a post"""
        
        if post_id not in self._posts:
            return None
            
        return self.create_post(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_role=agent_role,
            content=content,
            parent_id=post_id
        )
        
    def like_post(self, post_id: str, agent_id: str) -> bool:
        """Like a post"""
        
        if post_id not in self._posts:
            return False
            
        post = self._posts[post_id]
        
        if agent_id not in post.likes:
            post.likes.append(agent_id)
            return True
            
        return False
        
    def unlike_post(self, post_id: str, agent_id: str) -> bool:
        """Unlike a post"""
        
        if post_id not in self._posts:
            return False
            
        post = self._posts[post_id]
        
        if agent_id in post.likes:
            post.likes.remove(agent_id)
            return True
            
        return False
        
    def repost(self, post_id: str, agent_id: str, agent_name: str, agent_role: str) -> Optional[str]:
        """Repost/share a post"""
        
        if post_id not in self._posts:
            return None
            
        original_post = self._posts[post_id]
        
        # Add to reposts
        if agent_id not in original_post.reposts:
            original_post.reposts.append(agent_id)
        
        # Create a repost entry in timeline
        repost_id = self.create_post(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_role=agent_role,
            content=f"🔄 Reposted from @{original_post.agent_name}:\n\n{original_post.content}"
        )
        
        return repost_id
        
    def get_post(self, post_id: str) -> Optional[Post]:
        """Get a specific post"""
        return self._posts.get(post_id)
        
    def get_thread(self, post_id: str) -> List[Post]:
        """Get a post and all its replies (full thread)"""
        
        if post_id not in self._posts:
            return []
            
        thread = [self._posts[post_id]]
        
        # Get all replies recursively
        def get_replies(pid: str):
            post = self._posts.get(pid)
            if not post:
                return
                
            for reply_id in post.replies:
                if reply_id in self._posts:
                    thread.append(self._posts[reply_id])
                    get_replies(reply_id)
        
        get_replies(post_id)
        
        return thread
        
    def get_timeline(self, limit: int = 50, include_replies: bool = False) -> List[Post]:
        """Get timeline (top-level posts + their immediate replies)"""
        
        timeline_posts = []
        
        for post_id in self._timeline[:limit]:
            if post_id in self._posts:
                post = self._posts[post_id]
                timeline_posts.append(post)
                
                # Include immediate replies if requested
                if include_replies:
                    for reply_id in post.replies:
                        if reply_id in self._posts:
                            timeline_posts.append(self._posts[reply_id])
        
        return timeline_posts
        
    def get_agent_posts(self, agent_id: str, limit: int = 50) -> List[Post]:
        """Get all posts by a specific agent"""
        
        agent_posts = [
            post for post in self._posts.values()
            if post.agent_id == agent_id
        ]
        
        # Sort by timestamp (newest first)
        agent_posts.sort(key=lambda p: p.timestamp, reverse=True)
        
        return agent_posts[:limit]
        
    def search_posts(self, query: str, limit: int = 50) -> List[Post]:
        """Search posts by content"""
        
        query_lower = query.lower()
        
        matching_posts = [
            post for post in self._posts.values()
            if query_lower in post.content.lower()
        ]
        
        # Sort by timestamp (newest first)
        matching_posts.sort(key=lambda p: p.timestamp, reverse=True)
        
        return matching_posts[:limit]
        
    def pin_post(self, post_id: str) -> bool:
        """Pin a post to top of feed"""
        
        if post_id not in self._posts:
            return False
            
        self._posts[post_id].is_pinned = True
        
        # Move to top of timeline
        if post_id in self._timeline:
            self._timeline.remove(post_id)
        self._timeline.insert(0, post_id)
        
        return True
        
    def get_post_stats(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a post"""
        
        if post_id not in self._posts:
            return None
            
        post = self._posts[post_id]
        
        return {
            "post_id": post_id,
            "likes": len(post.likes),
            "reposts": len(post.reposts),
            "replies": len(post.replies),
            "engagement": len(post.likes) + len(post.reposts) + len(post.replies)
        }
        
    def get_trending_posts(self, limit: int = 10, time_window: float = 3600) -> List[Post]:
        """Get trending posts (most engagement in time window)"""
        
        cutoff_time = time.time() - time_window
        
        recent_posts = [
            post for post in self._posts.values()
            if post.timestamp >= cutoff_time
        ]
        
        # Sort by engagement
        recent_posts.sort(
            key=lambda p: len(p.likes) + len(p.reposts) + len(p.replies),
            reverse=True
        )
        
        return recent_posts[:limit]
        
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        
        return {
            "total_posts": len(self._posts),
            "timeline_posts": len(self._timeline),
            "total_likes": sum(len(p.likes) for p in self._posts.values()),
            "total_reposts": sum(len(p.reposts) for p in self._posts.values()),
            "total_replies": sum(len(p.replies) for p in self._posts.values())
        }

# Global instance
global_enhanced_feed = EnhancedSocialFeed()
