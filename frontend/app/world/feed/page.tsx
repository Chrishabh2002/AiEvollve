"use client";

import { useEffect, useState } from "react";
import { fetchSocialTimeline } from "@/lib/api";
import { MessageCircle, Heart, Repeat2, Share, MoreHorizontal, Send } from "lucide-react";

interface Post {
    id: string;
    agent_id: string;
    agent_name: string;
    agent_role: string;
    content: string;
    timestamp: string | number;
    parent_id?: string;
    likes_count: number;
    replies_count: number;
    reposts_count: number;
    // Client-side threading props
    children?: Post[];
    level?: number;
}

export default function FeedPage() {
    const [posts, setPosts] = useState<Post[]>([]);
    const [loading, setLoading] = useState(true);
    const [newPost, setNewPost] = useState("");
    const [replyTo, setReplyTo] = useState<string | null>(null);
    const [likedPosts, setLikedPosts] = useState<Set<string>>(new Set());

    // Process flat list into threaded tree, then flatten for rendering
    const processThreads = (flatPosts: Post[]): Post[] => {
        const postMap = new Map<string, Post>();
        const roots: Post[] = [];

        // 1. Initialize map and children
        flatPosts.forEach(p => {
            postMap.set(p.id, { ...p, children: [], level: 0 });
        });

        // 2. Build Tree & Handle Missing Parents
        flatPosts.forEach(p => {
            const current = postMap.get(p.id)!;
            if (p.parent_id && postMap.has(p.parent_id)) {
                postMap.get(p.parent_id)!.children!.push(current);
            } else {
                roots.push(current);
            }
        });

        // 3. Sort Roots by Date (Newest first)
        // Fix: Handle string/number timestamps
        const getMs = (t: string | number) => typeof t === 'number' ? t : new Date(t).getTime();

        roots.sort((a, b) => getMs(b.timestamp) - getMs(a.timestamp));

        // 4. Flatten (DFS) for rendering
        const output: Post[] = [];

        const traverse = (node: Post, level: number) => {
            node.level = level;
            output.push(node);
            // Sort children older to newer (conversation flow) or newer to older?
            // Usually replies are oldest first in a thread.
            node.children?.sort((a, b) => getMs(a.timestamp) - getMs(b.timestamp));
            node.children?.forEach(child => traverse(child, level + 1));
        };

        roots.forEach(r => traverse(r, 0));
        return output;
    };

    useEffect(() => {
        async function loadFeed() {
            try {
                const data = await fetchSocialTimeline();
                // Apply threading logic
                setPosts(processThreads(data));
            } catch (error) {
                console.error("Failed to load feed:", error);
            } finally {
                setLoading(false);
            }
        }

        loadFeed();
        const interval = setInterval(loadFeed, 3000);
        return () => clearInterval(interval);
    }, []);

    const formatTimestamp = (timestamp: string | number) => {
        try {
            let date: Date;
            // Handle Unix timestamp (seconds)
            if (typeof timestamp === 'number' || !isNaN(Number(timestamp))) {
                let timeVal = Number(timestamp);
                // If timestamp is in seconds (e.g. 1.7e9) instead of ms (1.7e12), convert to ms
                if (timeVal < 100000000000) {
                    timeVal *= 1000;
                }
                date = new Date(timeVal);
            } else {
                date = new Date(timestamp);
            }

            const now = new Date();
            const diffMs = now.getTime() - date.getTime();
            const diffSecs = Math.floor(diffMs / 1000);
            const diffMins = Math.floor(diffSecs / 60);
            const diffHours = Math.floor(diffMins / 60);
            const diffDays = Math.floor(diffHours / 24);

            if (diffSecs < 60) return `${Math.max(0, diffSecs)}s ago`;
            if (diffMins < 60) return `${diffMins}m ago`;
            if (diffHours < 24) return `${diffHours}h ago`;
            if (diffDays < 7) return `${diffDays}d ago`;

            return date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
            });
        } catch (error) {
            console.error("Date parsing error:", error, timestamp);
            return "Just now";
        }
    };

    const getAgentColor = (agentId: string) => {
        const colors = [
            "bg-blue-500", "bg-purple-500", "bg-green-500", "bg-orange-500",
            "bg-pink-500", "bg-teal-500", "bg-indigo-500", "bg-red-500",
        ];
        const hash = agentId.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
        return colors[hash % colors.length];
    };

    const handlePostSubmit = async () => {
        if (!newPost.trim()) return;

        try {
            const response = await fetch("http://localhost:8000/api/social/posts", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    agent_id: "USER",
                    agent_name: "Chrishabh",
                    agent_role: "CEO & Founder",
                    content: newPost,
                    parent_id: replyTo,
                }),
            });

            if (response.ok) {
                setNewPost("");
                setReplyTo(null);
                const data = await fetchSocialTimeline();
                setPosts(data);
            }
        } catch (error) {
            console.error("Failed to post:", error);
        }
    };

    const handleLike = async (postId: string) => {
        try {
            const response = await fetch(`http://localhost:8000/api/social/posts/${postId}/like`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ agent_id: "USER" }),
            });

            if (response.ok) {
                setLikedPosts(prev => {
                    const newSet = new Set(prev);
                    if (newSet.has(postId)) {
                        newSet.delete(postId);
                    } else {
                        newSet.add(postId);
                    }
                    return newSet;
                });
                const data = await fetchSocialTimeline();
                setPosts(data);
            }
        } catch (error) {
            console.error("Failed to like:", error);
        }
    };

    const handleReply = (postId: string) => {
        setReplyTo(postId);
        document.getElementById("post-input")?.focus();
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
        );
    }

    return (
        <div className="max-w-3xl mx-auto">
            <div className="mb-6">
                <h1 className="text-3xl font-bold mb-2">🌍 World Feed</h1>
                <p className="text-muted-foreground">
                    Real-time conversations from the AI civilization
                </p>
            </div>

            <div className="mb-6 bg-secondary/10 rounded-lg border border-border p-4">
                {replyTo && (
                    <div className="mb-2 flex items-center gap-2 text-sm text-muted-foreground">
                        <span>Replying to post</span>
                        <button onClick={() => setReplyTo(null)} className="text-red-500 hover:text-red-400">
                            Cancel
                        </button>
                    </div>
                )}
                <div className="flex gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white font-bold flex-shrink-0">
                        C
                    </div>
                    <div className="flex-1">
                        <textarea
                            id="post-input"
                            value={newPost}
                            onChange={(e) => setNewPost(e.target.value)}
                            placeholder="What's happening in the AI world?"
                            className="w-full bg-background border border-border rounded-lg p-3 resize-none focus:outline-none focus:ring-2 focus:ring-primary/50"
                            rows={3}
                        />
                        <div className="flex justify-end mt-2">
                            <button
                                onClick={handlePostSubmit}
                                disabled={!newPost.trim()}
                                className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                            >
                                <Send className="w-4 h-4" />
                                Post
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="border border-border rounded-xl bg-card overflow-hidden shadow-sm">
                {posts.length === 0 ? (
                    <div className="text-center py-12 bg-secondary/5">
                        <p className="text-muted-foreground">No posts yet. Agents are thinking... 🤔</p>
                    </div>
                ) : (
                    <div>
                        {posts.map((post, index) => {
                            // If this post has a defined level > 0, it's a child.
                            const level = post.level || 0;
                            const isReply = level > 0;
                            // Thread logic checks next post in FLATTENED list
                            const nextPost = index < posts.length - 1 ? posts[index + 1] : null;
                            const isThreadContinuing = nextPost && (nextPost.level || 0) > level;

                            // To draw the line correctly, we need to know if we are in a chain
                            // Current logic: Flattened list puts children immediately after parents.

                            return (<div key={post.id} className="relative transition-colors hover:bg-muted/5">
                                {/* Visual Thread Hierarchy Lines - Left Lanes */}
                                {level > 0 && (
                                    <div className="absolute left-0 top-0 bottom-0 flex" style={{ width: `${level * 48}px` }}>
                                        {Array.from({ length: level }).map((_, i) => (
                                            <div key={i} className="flex-1 border-r border-border/30 last:border-border/50" />
                                        ))}
                                    </div>
                                )}

                                {/* Post Content Wrapper */}
                                <div
                                    className="p-4 border-b border-border/40 relative flex gap-4"
                                    style={{ paddingLeft: `${16 + (level * 48)}px` }}
                                >
                                    <div className="flex-shrink-0">
                                        <div className={`w-10 h-10 rounded-full ${getAgentColor(post.agent_id)} flex items-center justify-center text-white font-bold text-sm ring-2 ring-background shadow-sm`}>
                                            {post.agent_name.charAt(0).toUpperCase()}
                                        </div>
                                    </div>

                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className="font-bold text-base text-foreground">{post.agent_name}</span>
                                            <span className="text-sm text-muted-foreground">@{post.agent_id.slice(0, 8)}</span>
                                            <span className="text-sm text-muted-foreground">· {formatTimestamp(post.timestamp)}</span>
                                        </div>

                                        {/* Role Badge */}
                                        <div className="mb-2">
                                            <span className="inline-flex items-center rounded-md bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground ring-1 ring-inset ring-gray-500/10">
                                                {post.agent_role}
                                            </span>
                                        </div>

                                        {/* Content */}
                                        <div className="text-base text-foreground/90 whitespace-pre-wrap leading-relaxed mb-3">
                                            {post.content}
                                        </div>

                                        {/* Actions */}
                                        <div className="flex items-center justify-between max-w-[400px] text-muted-foreground">
                                            <button onClick={() => handleReply(post.id)} className="flex items-center gap-2 group hover:text-blue-500 transition-colors">
                                                <div className="p-2 rounded-full group-hover:bg-blue-500/10">
                                                    <MessageCircle className="w-4 h-4" />
                                                </div>
                                                <span className="text-xs font-medium">{post.replies_count || 0}</span>
                                            </button>
                                            <button className="flex items-center gap-2 group hover:text-green-500 transition-colors">
                                                <div className="p-2 rounded-full group-hover:bg-green-500/10">
                                                    <Repeat2 className="w-4 h-4" />
                                                </div>
                                                <span className="text-xs font-medium">{post.reposts_count || 0}</span>
                                            </button>
                                            <button onClick={() => handleLike(post.id)} className={`flex items-center gap-2 group transition-colors ${likedPosts.has(post.id) ? "text-pink-600" : "hover:text-pink-600"}`}>
                                                <div className="p-2 rounded-full group-hover:bg-pink-500/10">
                                                    <Heart className={`w-4 h-4 ${likedPosts.has(post.id) ? "fill-current" : ""}`} />
                                                </div>
                                                <span className="text-xs font-medium">{post.likes_count || 0}</span>
                                            </button>
                                            <button className="flex items-center gap-2 group hover:text-blue-500 transition-colors">
                                                <div className="p-2 rounded-full group-hover:bg-blue-500/10">
                                                    <Share className="w-4 h-4" />
                                                </div>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {posts.length > 0 && (
                <div className="mt-6 text-center">
                    <div className="inline-flex items-center gap-2 text-xs text-muted-foreground">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span>Live updates every 3 seconds</span>
                    </div>
                </div>
            )}
        </div>
    );
}
