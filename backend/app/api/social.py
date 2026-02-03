"""
Enhanced Social Feed API - Twitter/X Style
Threaded conversations with replies, likes, reposts
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from backend.app.state import global_state

router = APIRouter(prefix="/social", tags=["social"])

# === REQUEST MODELS ===

class CreatePostRequest(BaseModel):
    agent_id: str
    agent_name: str
    agent_role: str
    content: str
    parent_id: Optional[str] = None
    is_idea: bool = False
    idea_id: Optional[str] = None
    attachments: List[Dict[str, Any]] = []

class ReplyRequest(BaseModel):
    post_id: str
    agent_id: str
    agent_name: str
    agent_role: str
    content: str

class LikeRequest(BaseModel):
    post_id: str
    agent_id: str

class RepostRequest(BaseModel):
    post_id: str
    agent_id: str
    agent_name: str
    agent_role: str

# === POSTS ===

@router.post("/posts")
async def create_post(request: CreatePostRequest) -> Dict[str, Any]:
    """Create a new post"""
    kernel = global_state.get_kernel()
    if not kernel:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    
    from kernel.enhanced_social import global_enhanced_feed
    
    post_id = global_enhanced_feed.create_post(
        agent_id=request.agent_id,
        agent_name=request.agent_name,
        agent_role=request.agent_role,
        content=request.content,
        parent_id=request.parent_id,
        is_idea=request.is_idea,
        idea_id=request.idea_id,
        attachments=request.attachments
    )
    
    return {"post_id": post_id, "status": "posted"}

@router.get("/posts/{post_id}")
async def get_post(post_id: str) -> Dict[str, Any]:
    """Get a specific post"""
    from kernel.enhanced_social import global_enhanced_feed
    
    post = global_enhanced_feed.get_post(post_id)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {
        "id": post.id,
        "agent_id": post.agent_id,
        "agent_name": post.agent_name,
        "agent_role": post.agent_role,
        "content": post.content,
        "timestamp": post.timestamp,
        "parent_id": post.parent_id,
        "likes": post.likes,
        "likes_count": len(post.likes),
        "reposts": post.reposts,
        "reposts_count": len(post.reposts),
        "replies": post.replies,
        "replies_count": len(post.replies),
        "is_idea": post.is_idea,
        "idea_id": post.idea_id,
        "attachments": post.attachments,
        "is_pinned": post.is_pinned
    }

@router.get("/timeline")
async def get_timeline(limit: int = 50, include_replies: bool = True) -> List[Dict[str, Any]]:
    """Get timeline (Twitter/X style feed)"""
    from kernel.enhanced_social import global_enhanced_feed
    
    posts = global_enhanced_feed.get_timeline(limit=limit, include_replies=include_replies)
    
    return [
        {
            "id": post.id,
            "agent_id": post.agent_id,
            "agent_name": post.agent_name,
            "agent_role": post.agent_role,
            "content": post.content,
            "timestamp": post.timestamp,
            "parent_id": post.parent_id,
            "likes_count": len(post.likes),
            "reposts_count": len(post.reposts),
            "replies_count": len(post.replies),
            "is_idea": post.is_idea,
            "idea_id": post.idea_id,
            "is_pinned": post.is_pinned,
            "is_announcement": post.is_announcement
        }
        for post in posts
    ]

@router.get("/thread/{post_id}")
async def get_thread(post_id: str) -> List[Dict[str, Any]]:
    """Get full thread (post + all nested replies)"""
    from kernel.enhanced_social import global_enhanced_feed
    
    thread = global_enhanced_feed.get_thread(post_id)
    
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    return [
        {
            "id": post.id,
            "agent_id": post.agent_id,
            "agent_name": post.agent_name,
            "agent_role": post.agent_role,
            "content": post.content,
            "timestamp": post.timestamp,
            "parent_id": post.parent_id,
            "likes_count": len(post.likes),
            "reposts_count": len(post.reposts),
            "replies_count": len(post.replies),
            "is_idea": post.is_idea
        }
        for post in thread
    ]

# === REPLIES ===

@router.post("/reply")
async def reply_to_post(request: ReplyRequest) -> Dict[str, Any]:
    """Reply to a post"""
    from kernel.enhanced_social import global_enhanced_feed
    
    reply_id = global_enhanced_feed.reply_to_post(
        post_id=request.post_id,
        agent_id=request.agent_id,
        agent_name=request.agent_name,
        agent_role=request.agent_role,
        content=request.content
    )
    
    if not reply_id:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {"reply_id": reply_id, "status": "replied"}

# === LIKES ===

@router.post("/like")
async def like_post(request: LikeRequest) -> Dict[str, Any]:
    """Like a post"""
    from kernel.enhanced_social import global_enhanced_feed
    
    success = global_enhanced_feed.like_post(request.post_id, request.agent_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to like post")
    
    return {"status": "liked"}

@router.post("/unlike")
async def unlike_post(request: LikeRequest) -> Dict[str, Any]:
    """Unlike a post"""
    from kernel.enhanced_social import global_enhanced_feed
    
    success = global_enhanced_feed.unlike_post(request.post_id, request.agent_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to unlike post")
    
    return {"status": "unliked"}

# === REPOSTS ===

@router.post("/repost")
async def repost_post(request: RepostRequest) -> Dict[str, Any]:
    """Repost/share a post"""
    from kernel.enhanced_social import global_enhanced_feed
    
    repost_id = global_enhanced_feed.repost(
        post_id=request.post_id,
        agent_id=request.agent_id,
        agent_name=request.agent_name,
        agent_role=request.agent_role
    )
    
    if not repost_id:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {"repost_id": repost_id, "status": "reposted"}

# === AGENT POSTS ===

@router.get("/agent/{agent_id}/posts")
async def get_agent_posts(agent_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get all posts by an agent"""
    from kernel.enhanced_social import global_enhanced_feed
    
    posts = global_enhanced_feed.get_agent_posts(agent_id, limit=limit)
    
    return [
        {
            "id": post.id,
            "content": post.content,
            "timestamp": post.timestamp,
            "parent_id": post.parent_id,
            "likes_count": len(post.likes),
            "reposts_count": len(post.reposts),
            "replies_count": len(post.replies)
        }
        for post in posts
    ]

# === SEARCH ===

@router.get("/search")
async def search_posts(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Search posts"""
    from kernel.enhanced_social import global_enhanced_feed
    
    posts = global_enhanced_feed.search_posts(query, limit=limit)
    
    return [
        {
            "id": post.id,
            "agent_name": post.agent_name,
            "content": post.content,
            "timestamp": post.timestamp,
            "likes_count": len(post.likes),
            "replies_count": len(post.replies)
        }
        for post in posts
    ]

# === TRENDING ===

@router.get("/trending")
async def get_trending(limit: int = 10, hours: int = 1) -> List[Dict[str, Any]]:
    """Get trending posts"""
    from kernel.enhanced_social import global_enhanced_feed
    
    time_window = hours * 3600
    posts = global_enhanced_feed.get_trending_posts(limit=limit, time_window=time_window)
    
    return [
        {
            "id": post.id,
            "agent_name": post.agent_name,
            "content": post.content,
            "timestamp": post.timestamp,
            "likes_count": len(post.likes),
            "reposts_count": len(post.reposts),
            "replies_count": len(post.replies),
            "engagement": len(post.likes) + len(post.reposts) + len(post.replies)
        }
        for post in posts
    ]

# === STATS ===

@router.get("/posts/{post_id}/stats")
async def get_post_stats(post_id: str) -> Dict[str, Any]:
    """Get post statistics"""
    from kernel.enhanced_social import global_enhanced_feed
    
    stats = global_enhanced_feed.get_post_stats(post_id)
    
    if not stats:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return stats

@router.get("/stats")
async def get_feed_stats() -> Dict[str, Any]:
    """Get overall feed statistics"""
    from kernel.enhanced_social import global_enhanced_feed
    
    return global_enhanced_feed.to_dict()

# === PIN ===

@router.post("/posts/{post_id}/pin")
async def pin_post(post_id: str) -> Dict[str, Any]:
    """Pin a post"""
    from kernel.enhanced_social import global_enhanced_feed
    
    success = global_enhanced_feed.pin_post(post_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {"status": "pinned"}
