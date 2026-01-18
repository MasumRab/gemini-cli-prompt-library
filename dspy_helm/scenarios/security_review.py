"""
Security Code Review Scenario.

Maps to: commands/code-review/security.toml
Category: Code Review & Analysis
"""

from typing import List, Dict, Any, TYPE_CHECKING
from .base import BaseScenario, ScenarioRegistry

if TYPE_CHECKING:
    import dspy


@ScenarioRegistry.register("security_review")
class SecurityReviewScenario(BaseScenario):
    """Scenario for evaluating security code review prompts."""

    INPUT_FIELDS = ["code"]
    OUTPUT_FIELDS = ["review"]

    def _load_raw_data(self) -> List[Dict[str, Any]]:
        """Load security review test cases."""
        import json
        from pathlib import Path

        data_path = Path(__file__).parent.parent / "data" / "security_review.jsonl"
        if data_path.exists():
            with open(data_path, "r") as f:
                data = [json.loads(line) for line in f if line.strip()]
                if data and "vars" in data[0]:
                    return [
                        {
                            "code": item["vars"]["code"],
                            "expected": item["vars"]["expected"],
                        }
                        for item in data
                    ]
                return data

        return [
            {
                "code": "SELECT * FROM users WHERE name = 'user_input'",
                "expected": "SQL injection",
            },
            {
                "code": "const apiKey = 'sk-12345abcdef';",
                "expected": "Hardcoded API key",
            },
            {
                "code": "function checkAuth(req) { return true; }",
                "expected": "Missing auth check",
            },
            {
                "code": "crypto.createHash('md5').update(password).digest('hex')",
                "expected": "MD5 insecure",
            },
            {
                "code": "fs.readFileSync(userFile, 'utf8');",
                "expected": "Path traversal",
            },
            {"code": "eval(userInput);", "expected": "Dangerous eval"},
            {
                "code": "document.innerHTML = userContent;",
                "expected": "XSS vulnerability",
            },
            {"code": "process.env.API_KEY in code", "expected": "Secret exposure"},
            {
                "code": "if (user.isAdmin) { grantAccess(); }",
                "expected": "Insecure reference",
            },
            {"code": "jwt.sign({user: id}, null);", "expected": "JWT no expiration"},
            {
                "code": "os.system('rm -rf ' + user_input)",
                "expected": "Command injection",
            },
            {
                "code": "new FileReader(userFile).readAsText(file)",
                "expected": "XXE vulnerability",
            },
            {"code": "requests.get(user_url)", "expected": "SSRF vulnerability"},
            {"code": "password.length > 6", "expected": "Weak password policy"},
            {
                "code": "if (user.admin) { showAdminPanel(); }",
                "expected": "Client-side check",
            },
            {
                "code": "sessionStorage.setItem('token', jwt)",
                "expected": "Token in localStorage",
            },
            {"code": "buffer.write(user_data)", "expected": "Buffer overflow"},
            {
                "code": "String.format('SELECT * FROM %s', table_name)",
                "expected": "SQL injection",
            },
            {"code": "XMLParser.parse(user_xml)", "expected": "XXE injection"},
            {"code": "Math.random() * 1000", "expected": "Insecure random"},
        ]

    def make_prompt(self, row: Dict[str, Any]) -> str:
        """Create prompt for security review."""
        return f"""# Security Code Review

Analyze the following code for security vulnerabilities:

```
{row["code"]}
```

## Required Output

1. **Vulnerability Identification**: List all security issues
2. **Severity Rating**: Critical/High/Medium/Low for each
3. **Remediation**: Specific, actionable fix for each issue
4. **Secure Alternative**: Show the code written securely

## Format

For each vulnerability:
- **Issue**: [description]
- **Severity**: [Critical/High/Medium/Low]
- **Fix**: [recommendation]
- **Example**: [secure code]

If no issues found, state: "No security vulnerabilities detected."
"""

    def metric(
        self, example: "dspy.Example", pred: "dspy.Prediction", trace=None
    ) -> float:
        """Evaluate security review quality."""
        expected_lower = example.expected.lower()
        pred_lower = str(pred.review).lower()

        if expected_lower in pred_lower:
            return 1.0

        vulnerability_terms = [
            "sql injection",
            "xss",
            "csrf",
            "authentication",
            "authorization",
            "injection",
            "cryptograph",
            "hardcoded",
            "secret",
            "vulnerability",
            "insecure",
        ]

        matches = sum(1 for term in vulnerability_terms if term in pred_lower)

        return min(matches / 3, 1.0)
