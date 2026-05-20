import os
def fix_perform_audit():
    with open('scripts/perform_audit.py', 'r') as f:
        content = f.read()

    bad_block = """<<<<<<< HEAD
    audit_date = datetime.datetime.now(datetime.timezone.utc).strftime("%B %Y")
    date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y_%m_%d")
=======
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    audit_date = now_utc.strftime("%B %Y")
    date_str = now_utc.strftime("%Y_%m_%d")
>>>>>>> 092e920 (Fix CodeRabbit review comments)"""

    good_block = """    now_utc = datetime.datetime.now(datetime.timezone.utc)
    audit_date = now_utc.strftime("%B %Y")
    date_str = now_utc.strftime("%Y_%m_%d")"""

    content = content.replace(bad_block, good_block)
    with open('scripts/perform_audit.py', 'w') as f:
        f.write(content)

fix_perform_audit()
