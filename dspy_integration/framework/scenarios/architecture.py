"""
Scenario for system architecture design.

This module defines the ArchitectureScenario for evaluating system architecture design tasks.
"""

from typing import List, Dict, Any, Tuple, Optional
from dspy import Example
from .base import ScenarioRegistry, BaseScenario


@ScenarioRegistry.register("architecture")
class ArchitectureScenario(BaseScenario):
    """
    Scenario for system architecture design tasks.

    This scenario handles the evaluation of architecture design modules
    by providing training/validation data and evaluation metrics.
    """

    INPUT_FIELDS = ["requirement_description"]
    OUTPUT_FIELDS = ["architecture_design", "components", "data_flow"]

    def __init__(self):
        """Initialize the ArchitectureScenario."""
        self.train_data = []
        self.val_data = []
        self._load_data()

    def _load_raw_data(self) -> List[Dict[str, Any]]:
        """
        Load raw data for the architecture scenario.
        
        Returns:
            List of dictionaries containing requirement descriptions and architecture designs
        """
        # Sample data for training and validation
        sample_data = [
            {
                "requirement_description": "Design a microservice architecture for an e-commerce platform.",
                "architecture_design": "# E-Commerce Microservice Architecture\n\n## Services:\n- User Service (authentication, profiles)\n- Product Catalog Service\n- Order Management Service\n- Payment Service\n- Inventory Service\n- Notification Service\n\n## Communication:\n- REST APIs for synchronous calls\n- Message queues for asynchronous processing\n\n## Data Storage:\n- User data: PostgreSQL\n- Product catalog: MongoDB\n- Orders: PostgreSQL\n- Logs: Elasticsearch",
                "components": ["User Service", "Product Catalog Service", "Order Management Service", "Payment Service", "Inventory Service", "Notification Service"],
                "data_flow": "User -> API Gateway -> Services -> Databases, Events -> Message Queue -> Services"
            },
            {
                "requirement_description": "Design a scalable architecture for a real-time chat application.",
                "architecture_design": "# Real-Time Chat Application Architecture\n\n## Components:\n- WebSocket Server (Socket.io/Node.js)\n- Message Broker (Redis)\n- User Presence Service\n- Message History Service\n- Load Balancer\n\n## Scaling:\n- Horizontal scaling of WebSocket servers\n- Redis cluster for message brokering\n- Database sharding for message history\n\n## Security:\n- JWT authentication\n- Rate limiting\n- Message encryption",
                "components": ["WebSocket Server", "Message Broker", "User Presence Service", "Message History Service", "Load Balancer"],
                "data_flow": "Client -> Load Balancer -> WebSocket Server -> Redis -> Client, Messages -> DB Storage"
            }
        ]
        return sample_data

    def _load_data(self):
        """
        Load and split data into train and validation sets.
        """
        raw_data = self._load_raw_data()
        
        # Simple split: 80% train, 20% validation
        split_idx = int(len(raw_data) * 0.8)
        self.train_data = [Example(**item).with_inputs(*self.INPUT_FIELDS) for item in raw_data[:split_idx]]
        self.val_data = [Example(**item).with_inputs(*self.INPUT_FIELDS) for item in raw_data[split_idx:]]

    def load_data(self) -> Tuple[List[Example], List[Example]]:
        """
        Load training and validation data.
        
        Returns:
            Tuple of (train_data, val_data) lists of Examples
        """
        return self.train_data, self.val_data

    def metric(
        self,
        example: "dspy.Example",
        pred: "dspy.Prediction",
        trace: Optional[Any] = None,
    ) -> float:
        """
        Evaluate the quality of an architecture design.

        Scoring criteria:
        - Completeness (0-10)
        - Scalability considerations (0-10)
        - Security considerations (0-10)
        - Component identification (0-10)
        - Data flow clarity (0-10)
        Total: 0-50

        Args:
            example: Ground truth example
            pred: Predicted result
            trace: Optional trace information

        Returns:
            Score from 0-50
        """
        # Convert pred to dict if it's a DSPy prediction object
        if hasattr(pred, 'architecture_design'):
            design = getattr(pred, 'architecture_design', '')
            components = getattr(pred, 'components', [])
            data_flow = getattr(pred, 'data_flow', '')
        else:
            # Fallback to string representation
            design = str(pred)
            components = []
            data_flow = ""

        score = 0

        # Completeness: Check for headers and sections
        if design.startswith("#"):
            score += 2
        if "##" in design:
            score += 2

        # Components: Check for component identification
        if isinstance(components, list) and len(components) > 0:
            score += 5  # Significant weight for identifying components

        # Scalability: Check for scalability-related terms
        if any(term in design.lower() for term in ["scale", "scaling", "horizontal", "vertical", "cluster", "shard"]):
            score += 3

        # Security: Check for security-related terms
        if any(term in design.lower() for term in ["security", "auth", "encrypt", "jwt", "rate limiting", "firewall"]):
            score += 3

        # Data flow: Check if data flow is described
        if data_flow and len(data_flow) > 10:  # Reasonable length for data flow
            score += 5  # Significant weight for data flow

        # Architecture patterns: Check for pattern-related terms
        if any(term in design.lower() for term in ["microservice", "monolith", "event", "cqrs", "layer", "tier"]):
            score += 3

        # Communication: Check for communication methods
        if any(term in design.lower() for term in ["rest", "graphql", "grpc", "message", "queue", "websocket"]):
            score += 3

        # Storage: Check for storage solutions
        if any(term in design.lower() for term in ["database", "sql", "nosql", "postgres", "mongo", "redis"]):
            score += 3

        # Performance: Check for performance considerations
        if any(term in design.lower() for term in ["performance", "cache", "cdn", "load balancer", "latency"]):
            score += 3

        # Monitoring: Check for monitoring terms
        if any(term in design.lower() for term in ["monitor", "log", "metrics", "alert", "observability"]):
            score += 2

        # Ensure score is within bounds
        min_score = max(score, 5)  # Minimum score of 5
        return min(min_score, 50)

    def make_prompt(self, row: Dict[str, Any]) -> str:
        """
        Create an architecture design prompt from a data row.

        Args:
            row: Dictionary containing requirement description

        Returns:
            Formatted prompt string
        """
        return f"Design a system architecture for the following requirements:\n\n{row['requirement_description']}"


# For backward compatibility
def get_architecture_scenario():
    """Get an instance of the ArchitectureScenario."""
    return ArchitectureScenario()