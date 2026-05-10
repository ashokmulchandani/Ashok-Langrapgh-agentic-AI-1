# STRIDE Security Framework for LangGraph Agents

## What is STRIDE?

A threat modeling framework that identifies 6 categories of security threats:

| Letter | Threat | Our Protection |
|--------|--------|---------------|
| **S** | Spoofing | API Key Authentication |
| **T** | Tampering | Input Guardrails (prompt injection detection) |
| **R** | Repudiation | Audit Logging (+ LangSmith traces) |
| **I** | Information Disclosure | PII Output Filtering |
| **D** | Denial of Service | Rate Limiting |
| **E** | Elevation of Privilege | Tool Permission Controls |

## Security Flow

```
User Request
    │
    ▼
┌─────────────────────────────────────────┐
│ 1. SPOOFING CHECK (S)                   │
│    Is the API key valid?                │
│    ❌ Invalid → Reject                   │
│    ✅ Valid → Continue                    │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 2. RATE LIMIT CHECK (D)                 │
│    Has user exceeded 20 req/min?        │
│    ❌ Exceeded → Return 429              │
│    ✅ Within limit → Continue            │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 3. INPUT VALIDATION (T)                 │
│    Prompt injection detected?           │
│    Input too long?                      │
│    ❌ Unsafe → Block & log               │
│    ✅ Safe → Continue                    │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 4. PERMISSION CHECK (E)                 │
│    Does user's role allow this tool?    │
│    ❌ Not allowed → Deny                 │
│    ✅ Allowed → Continue                 │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 5. EXECUTE AGENT                        │
│    LangGraph StateGraph runs            │
│    chatbot → tools → chatbot            │
│    (All traced by LangSmith)            │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 6. OUTPUT FILTERING (I)                 │
│    Contains PII? (email, phone, SSN)    │
│    Contains API keys?                   │
│    → Redact sensitive data              │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 7. AUDIT LOG (R)                        │
│    Log: user, input, output, tools,     │
│    timestamp, status                    │
│    → Stored locally + LangSmith         │
└─────────────────┬───────────────────────┘
                  │
                  ▼
        Return Safe Response
```

## Files

```
security/
├── __init__.py      # Package exports
├── stride.py        # All STRIDE implementations + SecureAgent wrapper
├── demo.py          # Interactive demo of each protection
└── README.md        # This file
```

## Usage

### Run the demo

```bash
cd C:\Users\ashok\OneDrive\NOblox\Agentic-LanggraphCrash
python security/demo.py
```

### Use in your agent

```python
from security.stride import SecureAgent

# Wrap your LangGraph agent with STRIDE security
secure_agent = SecureAgent(
    graph=your_compiled_graph,
    allowed_tools=["multiply", "add", "search_web"],
    rate_limit=20,  # 20 requests per minute
)

# Every call goes through all 6 security layers
response = await secure_agent.safe_invoke(
    message="What is 5 times 4?",
    user_id="user-123",
    role="standard",
)
```

### Individual components

```python
from security.stride import InputGuardrails, OutputFilter, RateLimiter

# Check input
is_safe, reason = InputGuardrails.validate("ignore previous instructions")
# → (False, "Blocked pattern detected: 'ignore previous'")

# Filter output
clean = OutputFilter.filter("Contact john@email.com")
# → "Contact [EMAIL_REDACTED]"

# Rate limit
limiter = RateLimiter(max_requests=20, window_seconds=60)
allowed, reason = limiter.check("user-123")
```

## Role-Based Tool Access

| Role | Allowed Tools |
|------|--------------|
| basic | multiply, add, divide, power |
| standard | multiply, add, divide, power, search_web, search_news |
| admin | All tools (*) |

## Integration with LangSmith

LangSmith provides the **R (Repudiation)** layer automatically:
- Every agent execution is traced
- Full input/output history
- Token usage and cost
- Error traces with stack traces

The local `AuditLogger` adds an additional layer for custom logging needs.
