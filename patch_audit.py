with open("scripts/perform_audit.py", "r") as f:
    content = f.read()

content = content.replace("""<<<<<<< HEAD
    audit_date = datetime.datetime.now(datetime.timezone.utc).strftime("%B %Y")
    date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y_%m_%d")
=======
    audit_date = datetime.datetime.now().strftime("%B %Y")
    date_str = datetime.datetime.now().strftime("%Y_%m_%d")
>>>>>>> a01c22e (feat: enable global DSPy integration installation via gemini prompt)""", """    audit_date = datetime.datetime.now(datetime.timezone.utc).strftime("%B %Y")
    date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y_%m_%d")""")

with open("scripts/perform_audit.py", "w") as f:
    f.write(content)
