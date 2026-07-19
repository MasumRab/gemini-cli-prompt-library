# Jules API Client Update

The Jules API client has been upgraded to a class-based architecture to support professional-grade operations.

## Key Changes
- **Standardized Key:** Switched to `JULES_API_KEY` (previously `JULES_API_KET`).
- **Resilience:** Added exponential backoff for 429 and 5xx errors.
- **Scalability:** Optimized pagination for large session histories.
- **Convenience:** Added `get_session`, `send_message`, and `approve_plan` convenience methods.

## Migration Guide
If you were using the old `jules_request` function directly, you should switch to the `JulesAPIClient` class:

**Old:**
```python
from jules_api_client import jules_request
res = jules_request("sessions/123")
```

**New:**
```python
from tools.api.jules_api_client import JulesAPIClient
client = JulesAPIClient()
res = client.get_session("123")
```

The old `jules_request` is still available for backward compatibility but is deprecated.
