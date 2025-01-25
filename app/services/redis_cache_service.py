import json
import redis
from typing import Optional, Dict, Any

redis_client = redis.Redis(host='redis', port=6379, db=0)

def generate_post_key(post_id: int) -> str:
    return f"post:{post_id}"

def generate_posts_list_key(filters: Optional[Dict[str, Any]] = None) -> str:
    if not filters:
        return "posts:list:default"
    
    filter_parts = []
    for key, value in sorted(filters.items()):
        if value is not None:
            filter_parts.append(f"{key}:{value}")
    
    return f"posts:list:{':'.join(filter_parts)}"

def cache_post(post: Dict[str, Any]) -> None:
    key = generate_post_key(post['id'])
    redis_client.setex(key, 3600, json.dumps(post))

def cache_posts_list(posts: list, filters: Optional[Dict[str, Any]] = None) -> None:
    key = generate_posts_list_key(filters)
    redis_client.setex(key, 3600, json.dumps(posts))

def get_cached_post(post_id: int) -> Optional[Dict[str, Any]]:
    key = generate_post_key(post_id)
    cached_post = redis_client.get(key)
    return json.loads(cached_post) if cached_post else None

def get_cached_posts_list(filters: Optional[Dict[str, Any]] = None) -> Optional[list]:
    key = generate_posts_list_key(filters)
    cached_posts = redis_client.get(key)
    return json.loads(cached_posts) if cached_posts else None

def invalidate_post_cache(post_id: int) -> None:
    key = generate_post_key(post_id)
    redis_client.delete(key)

def invalidate_posts_list_cache() -> None:
    for key in redis_client.keys("posts:list:*"):
        redis_client.delete(key)