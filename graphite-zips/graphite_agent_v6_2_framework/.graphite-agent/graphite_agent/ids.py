class IdFactory:
    def __init__(self):
        self.rel = 0
        self.triage = 0
        self.exec = 0

    def relationship_id(self):
        self.rel += 1
        return f"rel-{self.rel:06d}"

    def triage_id(self):
        self.triage += 1
        return f"triage-{self.triage:06d}"

    def execution_id(self):
        self.exec += 1
        return f"exec-{self.exec:06d}"
