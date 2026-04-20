with open('scripts/perform_audit.py', 'r') as f:
    content = f.read()

content = content.replace('''<<<<<<< HEAD
    audit_date = datetime.datetime.now(datetime.timezone.utc).strftime("%B %Y")
    date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y_%m_%d")
=======
    audit_date = datetime.datetime.now().strftime("%B %Y")
    date_str = datetime.datetime.now().strftime("%Y_%m_%d")
>>>>>>> 58ef874 (Fix flake8 linting errors and resolve SonarCloud duplication failure)''', '''    audit_date = datetime.datetime.now(datetime.timezone.utc).strftime("%B %Y")
    date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y_%m_%d")''')

with open('scripts/perform_audit.py', 'w') as f:
    f.write(content)
