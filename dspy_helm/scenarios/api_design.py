"""
API Design Scenario.

Maps to: commands/architecture/design-api.toml
Category: Architecture & Design
"""

import dspy

from typing import List, Dict, Any
from .base import BaseScenario, ScenarioRegistry


@ScenarioRegistry.register("api_design")
class APIDesignScenario(BaseScenario):
    """Scenario for evaluating API design prompts."""

    INPUT_FIELDS = ["requirements"]
    OUTPUT_FIELDS = ["design"]

    def _load_raw_data(self) -> List[Dict[str, Any]]:
        """Load API design test cases."""
        import json
        from pathlib import Path

        data_path = Path(__file__).parent.parent / "data" / "api_design.jsonl"
        if data_path.exists():
            with open(data_path, "r") as f:
                data = [json.loads(line) for line in f if line.strip()]
                if data and "input" in data[0] and "expected_output" in data[0]:
                    return [
                        {
                            "requirements": item["input"],
                            "design": item["expected_output"],
                        }
                        for item in data
                    ]
                return data

        return [
            {
                "requirements": "User management system with authentication",
                "design": "POST /users, GET /users/{id}, POST /auth/login",
            },
            {
                "requirements": "E-commerce with products, orders, payments",
                "design": "Products CRUD, Orders CRUD, Payment",
            },
            {
                "requirements": "Blog platform with posts, comments, users",
                "design": "Posts CRUD, Comments CRUD, Auth",
            },
            {
                "requirements": "File storage system with sharing",
                "design": "Files CRUD, Share, Download",
            },
            {
                "requirements": "Notification system with preferences",
                "design": "Notifications CRUD, Preferences",
            },
            {
                "requirements": "Real-time chat application",
                "design": "Messages CRUD, Channels, Presence",
            },
            {
                "requirements": "Analytics dashboard with reports",
                "design": "Reports CRUD, Metrics, Export",
            },
            {
                "requirements": "Search engine with filters",
                "design": "Search endpoint, Filters",
            },
            {
                "requirements": "Booking system with availability",
                "design": "Bookings CRUD, Availability",
            },
            {
                "requirements": "Inventory management system",
                "design": "Items CRUD, Stock, Suppliers",
            },
            {
                "requirements": "Task management with teams",
                "design": "Tasks CRUD, Teams, Assignments",
            },
            {
                "requirements": "Content management with versioning",
                "design": "Content CRUD, Versions",
            },
            {
                "requirements": "Subscription billing with plans",
                "design": "Plans CRUD, Subscriptions, Invoices",
            },
            {
                "requirements": "Multi-tenant forum system",
                "design": "Forums CRUD, Posts, Moderation",
            },
            {
                "requirements": "Device management IoT platform",
                "design": "Devices CRUD, Telemetry, Commands",
            },
            {
                "requirements": "Document collaboration with comments",
                "design": "Documents CRUD, Comments, Versions",
            },
            {
                "requirements": "Location services with geofencing",
                "design": "Locations CRUD, Geofences",
            },
            {
                "requirements": "Email marketing platform",
                "design": "Campaigns CRUD, Templates, Lists",
            },
            {
                "requirements": "Help desk ticketing system",
                "design": "Tickets CRUD, Comments",
            },
            {
                "requirements": "Social feed with recommendations",
                "design": "Posts CRUD, Feed, Follows",
            },
        ]

    def make_prompt(self, row: Dict[str, Any]) -> str:
        """Create prompt for API design."""
        return f"""# RESTful API Design

Design a comprehensive RESTful API for:

```
{row["requirements"]}
```

## API Design Requirements

### 1. Resource Modeling
- Identify main entities
- Define relationships
- Plan operations

### 2. HTTP Methods
- GET: Retrieve
- POST: Create
- PUT: Full update
- PATCH: Partial update
- DELETE: Remove

### 3. URL Structure
- Use nouns, not verbs
- Use plural forms
- Limit nesting to 2 levels
- Use kebab-case

### 4. Query Parameters
- Filtering: ?status=active
- Sorting: ?sort=created_at:desc
- Pagination: ?page=2&limit=20

### 5. Response Format

```json
{{
  "data": {{...}},
  "meta": {{
    "pagination": {{...}},
    "request_id": "..."
  }}
}}
```

### 6. Status Codes
- 200: OK
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Output Format

Provide:
1. **API Overview**: Base URL, authentication, version
2. **Endpoints Table**: Method, Path, Description
3. **Detailed Specs**: For each endpoint
4. **Request/Response Examples**
5. **Error Handling Guide**
"""

    def metric(
        self, example: "dspy.Example", pred: "dspy.Prediction", trace=None
    ) -> float:
        """Evaluate API design quality."""
        expected = example.design.lower()
        pred_text = str(pred.design).lower()
        if expected in pred_text:
            return 1.0
        return 0.0
