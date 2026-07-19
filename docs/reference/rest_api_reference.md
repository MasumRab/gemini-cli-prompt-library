# Jules API REST Reference

The Jules API uses REST over HTTPS with API key authentication.

## Base URL
```
https://jules.googleapis.com/v1alpha
```

## Authentication
All requests require the `X-Goog-Api-Key` header with your Jules API key.

```bash
-H "X-Goog-Api-Key: $JULES_API_KEY"
```

## Common Headers
- `Content-Type: application/json` (for POST/PUT/PATCH with body)
- `Accept: application/json` (optional, JSON is default)

## Endpoints

### Sessions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sessions?pageSize=N&pageToken=STR` | List sessions (paginated) |
| GET | `/sessions/{sessionId}` | Get session details |
| POST | `/sessions/{sessionId}:sendMessage` | Send a message to session |
| POST | `/sessions/{sessionId}:approvePlan` | Approve the current plan |

### Activities
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sessions/{sessionId}/activities?pageSize=N&pageToken=STR` | List session activities (paginated) |

## Request Body Formats

### Send Message
```json
{
  "prompt": "Your message here"
}
```

### Approve Plan
```json
{}
```

## Response Format
All successful responses return JSON objects. Error responses include HTTP status codes:
- 200: Success
- 400: Bad Request (invalid parameters or body)
- 401: Unauthorized (missing/invalid API key)
- 403: Forbidden (insufficient permissions)
- 404: Not Found (session not found)
- 429: Too Many Requests (rate limited)
- 5xx: Server Error

## Examples

### List Sessions (first page)
```bash
curl -s \
  -H "X-Goog-Api-Key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions?pageSize=10"
```

### Get Session Details
```bash
curl -s \
  -H "X-Goog-Api-Key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions/4065247280866720283"
```

### Send Message
```bash
curl -s -X POST \
  -H "X-Goog-Api-Key: $JULES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello from automated test"}' \
  "https://jules.googleapis.com/v1alpha/sessions/4065247280866720283:sendMessage"
```

Successful `sendMessage` responses have an empty body.

### Approve Plan
```bash
curl -s -X POST \
  -H "X-Goog-Api-Key: $JULES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "https://jules.googleapis.com/v1alpha/sessions/4065247280866720283:approvePlan"
```

## Notes
- Session IDs may be provided with or without the `sessions/` prefix (both work)
- All timestamps are in RFC3339 format (e.g., `2023-01-01T12:34:56.789Z`)
- For paging, use `nextPageToken` from previous response
- Rate limits apply; implement exponential backoff for 429 responses
