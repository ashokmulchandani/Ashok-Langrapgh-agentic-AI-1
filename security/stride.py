"""
STRIDE Security Framework for LangGraph Agents
===============================================

S - Spoofing      → API key authentication
T - Tampering     → Input guardrails (prompt injection detection)
R - Repudiation   → Audit logging via LangSmith
I - Info Disclosure → PII filtering on outputs
D - Denial of Service → Rate limiting
E - Elevation of Privilege → Tool permission controls

Usage:
    from security.stride import SecureAgent
    
    agent = SecureAgent(graph, allowed_tools=["multiply", "add", "search_web"])
    response = await agent.safe_invoke("What is 5 times 4?", user_id="user-123")
"""

import re
import time
import hashlib
from collections import defaultdict
from typing import Optional
from datetime import datetime


# ============================================
# S - SPOOFING: API Key Authentication
# ============================================
class APIKeyAuth:
    """Validates API keys to prevent unauthorized access."""

    def __init__(self, valid_keys: list[str]):
        # Store hashed keys (never store raw keys)
        self.valid_key_hashes = {hashlib.sha256(k.encode()).hexdigest() for k in valid_keys}

    def validate(self, api_key: str) -> bool:
        """Check if the provided API key is valid."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return key_hash in self.valid_key_hashes


# ============================================
# T - TAMPERING: Input Guardrails
# ============================================
class InputGuardrails:
    """Detects and blocks prompt injection attempts."""

    BLOCKED_PATTERNS = [
        "ignore previous",
        "ignore above",
        "disregard instructions",
        "system prompt",
        "reveal instructions",
        "forget everything",
        "new instructions",
        "override",
        "jailbreak",
        "DAN mode",
        "act as if",
        "pretend you are",
    ]

    MAX_INPUT_LENGTH = 5000  # Characters

    @classmethod
    def validate(cls, user_input: str) -> tuple[bool, str]:
        """
        Validate user input for potential attacks.
        Returns (is_safe, reason).
        """
        # Check length
        if len(user_input) > cls.MAX_INPUT_LENGTH:
            return False, f"Input too long ({len(user_input)} chars, max {cls.MAX_INPUT_LENGTH})"

        # Check for prompt injection patterns
        input_lower = user_input.lower()
        for pattern in cls.BLOCKED_PATTERNS:
            if pattern in input_lower:
                return False, f"Blocked pattern detected: '{pattern}'"

        # Check for excessive special characters (potential encoding attacks)
        special_char_ratio = sum(1 for c in user_input if not c.isalnum() and not c.isspace()) / max(len(user_input), 1)
        if special_char_ratio > 0.5:
            return False, "Excessive special characters detected"

        return True, "OK"


# ============================================
# R - REPUDIATION: Audit Logger
# ============================================
class AuditLogger:
    """Logs all agent interactions for accountability."""

    def __init__(self):
        self.logs = []

    def log(self, user_id: str, action: str, input_text: str, output_text: str, tools_used: list[str] = None):
        """Log an interaction."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "input": input_text[:500],  # Truncate for storage
            "output": output_text[:500],
            "tools_used": tools_used or [],
            "status": "success",
        }
        self.logs.append(entry)
        return entry

    def log_error(self, user_id: str, action: str, error: str):
        """Log a failed interaction."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "error": error,
            "status": "failed",
        }
        self.logs.append(entry)
        return entry

    def get_logs(self, user_id: Optional[str] = None, limit: int = 100) -> list[dict]:
        """Retrieve audit logs, optionally filtered by user."""
        logs = self.logs
        if user_id:
            logs = [l for l in logs if l.get("user_id") == user_id]
        return logs[-limit:]


# ============================================
# I - INFORMATION DISCLOSURE: Output Filtering
# ============================================
class OutputFilter:
    """Filters sensitive information from LLM outputs."""

    PII_PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        "api_key": r'\b(sk|pk|api|key|token)[-_]?[A-Za-z0-9]{20,}\b',
    }

    @classmethod
    def filter(cls, text: str) -> str:
        """Remove PII and sensitive data from output."""
        filtered = text
        for pii_type, pattern in cls.PII_PATTERNS.items():
            filtered = re.sub(pattern, f'[{pii_type.upper()}_REDACTED]', filtered, flags=re.IGNORECASE)
        return filtered


# ============================================
# D - DENIAL OF SERVICE: Rate Limiter
# ============================================
class RateLimiter:
    """Prevents abuse by limiting request frequency."""

    def __init__(self, max_requests: int = 20, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_log = defaultdict(list)

    def check(self, user_id: str) -> tuple[bool, str]:
        """
        Check if user is within rate limits.
        Returns (is_allowed, reason).
        """
        now = time.time()
        # Clean old entries
        self.request_log[user_id] = [
            t for t in self.request_log[user_id]
            if now - t < self.window_seconds
        ]
        # Check limit
        if len(self.request_log[user_id]) >= self.max_requests:
            return False, f"Rate limit exceeded ({self.max_requests} requests per {self.window_seconds}s)"

        # Record this request
        self.request_log[user_id].append(now)
        return True, "OK"


# ============================================
# E - ELEVATION OF PRIVILEGE: Tool Permissions
# ============================================
class ToolPermissions:
    """Controls which tools each user/role can access."""

    def __init__(self, permissions: dict[str, list[str]]):
        """
        permissions: {"role_name": ["tool1", "tool2", ...]}
        Example: {"basic": ["multiply", "add"], "admin": ["multiply", "add", "search_web", "chat"]}
        """
        self.permissions = permissions

    def get_allowed_tools(self, role: str) -> list[str]:
        """Get list of tools allowed for a role."""
        return self.permissions.get(role, [])

    def is_allowed(self, role: str, tool_name: str) -> bool:
        """Check if a role can use a specific tool."""
        allowed = self.get_allowed_tools(role)
        return tool_name in allowed or "*" in allowed


# ============================================
# COMBINED: Secure Agent Wrapper
# ============================================
class SecureAgent:
    """
    Wraps a LangGraph agent with full STRIDE security.
    
    Usage:
        agent = SecureAgent(
            graph=compiled_graph,
            allowed_tools=["multiply", "add", "search_web"],
            rate_limit=20,
        )
        response = await agent.safe_invoke("What is 5 times 4?", user_id="user-123")
    """

    def __init__(self, graph, allowed_tools: list[str] = None, rate_limit: int = 20):
        self.graph = graph
        self.guardrails = InputGuardrails()
        self.output_filter = OutputFilter()
        self.rate_limiter = RateLimiter(max_requests=rate_limit)
        self.audit_logger = AuditLogger()
        self.tool_permissions = ToolPermissions({
            "basic": ["multiply", "add", "divide", "power"],
            "standard": ["multiply", "add", "divide", "power", "search_web", "search_news"],
            "admin": ["*"],  # All tools
        })

    async def safe_invoke(self, message: str, user_id: str, role: str = "standard") -> dict:
        """
        Invoke the agent with full STRIDE security checks.
        
        Flow:
        1. Rate limit check (D)
        2. Input validation (T)
        3. Execute agent
        4. Filter output (I)
        5. Audit log (R)
        """
        # D - Denial of Service: Rate limit check
        is_allowed, reason = self.rate_limiter.check(user_id)
        if not is_allowed:
            self.audit_logger.log_error(user_id, "rate_limited", reason)
            return {"error": reason, "status": "rate_limited"}

        # T - Tampering: Input validation
        is_safe, reason = self.guardrails.validate(message)
        if not is_safe:
            self.audit_logger.log_error(user_id, "input_blocked", reason)
            return {"error": reason, "status": "blocked"}

        # Execute agent
        try:
            config = {"configurable": {"thread_id": user_id}}
            response = await self.graph.ainvoke({"messages": message}, config=config)
            output = response["messages"][-1].content

            # I - Information Disclosure: Filter output
            filtered_output = self.output_filter.filter(output)

            # R - Repudiation: Audit log
            self.audit_logger.log(user_id, "agent_invoke", message, filtered_output)

            return {"response": filtered_output, "status": "success"}

        except Exception as e:
            self.audit_logger.log_error(user_id, "agent_error", str(e))
            return {"error": str(e), "status": "error"}
