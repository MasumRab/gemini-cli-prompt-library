with open("tools/sessions/post_pr_feedback.py", "r") as f:
    content = f.read()

# I had already put import sys and import os and import re at top, why did it complain?
# ah, line 44 `import re` was missing from local scope maybe.
content = content.replace(
    "    import re\n    # Parse: https://github.com/owner/repo/pull/123",
    "    # Parse: https://github.com/owner/repo/pull/123",
)
content = content.replace("import sys\nimport os\nimport re\n", "")

# Let's just fix it properly
content = "import sys\nimport os\nimport re\n" + content.replace(
    "import sys\nimport os\nimport re\n", ""
)

with open("tools/sessions/post_pr_feedback.py", "w") as f:
    f.write(content)
