"""
Simple file-based session storage for development.
In production, use Redis or another persistent cache.
"""
import json
import os
from typing import Optional, Any
from datetime import datetime, timedelta
import asyncio
from pathlib import Path


class SessionStore:
    """File-based session storage that persists across server restarts."""
    
    def __init__(self, storage_path: str = ".sessions"):
        """Initialize the session store with a storage path."""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self._lock = asyncio.Lock()
        # Clean up expired sessions on initialization
        asyncio.create_task(self._cleanup_expired())
    
    async def set(self, key: str, value: Any, expire_seconds: int = 300) -> None:
        """Store a session value with expiration."""
        async with self._lock:
            file_path = self.storage_path / f"{key}.json"
            expiry = datetime.utcnow() + timedelta(seconds=expire_seconds)
            
            data = {
                "value": value,
                "expiry": expiry.isoformat()
            }
            
            with open(file_path, "w") as f:
                json.dump(data, f)
    
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a session value if it exists and hasn't expired."""
        async with self._lock:
            file_path = self.storage_path / f"{key}.json"
            
            if not file_path.exists():
                return None
            
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                
                expiry = datetime.fromisoformat(data["expiry"])
                if datetime.utcnow() > expiry:
                    # Session expired, remove it
                    file_path.unlink(missing_ok=True)
                    return None
                
                return data["value"]
            except (json.JSONDecodeError, KeyError, ValueError):
                # Corrupted file, remove it
                file_path.unlink(missing_ok=True)
                return None
    
    async def delete(self, key: str) -> None:
        """Delete a session value."""
        async with self._lock:
            file_path = self.storage_path / f"{key}.json"
            file_path.unlink(missing_ok=True)
    
    async def exists(self, key: str) -> bool:
        """Check if a session key exists and is valid."""
        value = await self.get(key)
        return value is not None
    
    async def _cleanup_expired(self) -> None:
        """Clean up expired session files periodically."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                async with self._lock:
                    for file_path in self.storage_path.glob("*.json"):
                        try:
                            with open(file_path, "r") as f:
                                data = json.load(f)
                            
                            expiry = datetime.fromisoformat(data["expiry"])
                            if datetime.utcnow() > expiry:
                                file_path.unlink(missing_ok=True)
                        except (json.JSONDecodeError, KeyError, ValueError):
                            # Corrupted file, remove it
                            file_path.unlink(missing_ok=True)
            except Exception:
                # Don't let cleanup errors crash the app
                pass


# Global session store instance
session_store = SessionStore()
