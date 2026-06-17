import subprocess
import os

class Git:
    def __init__(self, remote='origin', retries=2):
        self.remote = remote
        self.retries = retries

    def run(self, args, check=True, input_text=None):
        env = os.environ.copy()
        env['GIT_TERMINAL_PROMPT'] = '0'
        env['GRAPHITE_NO_INTERACTIVE'] = '1'
        last = None
        for i in range(max(1, self.retries + 1)):
            last = subprocess.run(args, input=input_text, capture_output=True, text=True, env=env)
            if last.returncode == 0:
                return last.stdout
            if not check:
                break
        if check and last and last.returncode != 0:
            raise subprocess.CalledProcessError(last.returncode, args, last.stdout, last.stderr)
        return last.stdout if last else ""

    def get_merge_base(self, a, b):
        return self.run(['git', 'merge-base', a, b]).strip()

    def is_ancestor(self, root, branch):
        res = subprocess.run(['git', 'merge-base', '--is-ancestor', root, branch])
        return res.returncode == 0

    def patch_ids(self, root, branch):
        out = self.run(['bash', '-c', f'git format-patch --stdout {root}..{branch} | git patch-id'])
        return [line.split()[0] for line in out.splitlines() if line.strip()]
