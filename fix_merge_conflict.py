with open("dspy_integration/framework/dispatcher.py", "r") as f:
    content = f.read()

bad_block = """<<<<<<< HEAD
        user_tokens = set(user_input_normalized.split())
        name_match_len = len(name_tokens.intersection(user_tokens))
        description_match_len = len(description_tokens.intersection(user_tokens))
=======
        name_match_len = len(name_tokens.intersection(user_input.split()))
        description_match_len = len(description_tokens.intersection(user_input.split()))
>>>>>>> 7d76daa (chore: fix linting issues and reapply prompt)"""

good_block = """        user_tokens = set(user_input_normalized.split())
        name_match_len = len(name_tokens.intersection(user_tokens))
        description_match_len = len(description_tokens.intersection(user_tokens))"""

content = content.replace(bad_block, good_block)

with open("dspy_integration/framework/dispatcher.py", "w") as f:
    f.write(content)


with open("scripts/perform_audit.py", "r") as f:
    content = f.read()

bad_block = """<<<<<<< HEAD
    audit_date = datetime.datetime.now(datetime.timezone.utc).strftime("%B %Y")
    date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y_%m_%d")
=======
    audit_date = datetime.datetime.now().strftime("%B %Y")
    date_str = datetime.datetime.now().strftime("%Y_%m_%d")
>>>>>>> 7d76daa (chore: fix linting issues and reapply prompt)"""

good_block = """    now_utc = datetime.datetime.now(datetime.timezone.utc)
    audit_date = now_utc.strftime("%B %Y")
    date_str = now_utc.strftime("%Y_%m_%d")"""

content = content.replace(bad_block, good_block)

with open("scripts/perform_audit.py", "w") as f:
    f.write(content)
