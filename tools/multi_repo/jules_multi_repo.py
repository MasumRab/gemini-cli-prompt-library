import argparse
import os
import subprocess


def analyze_repos(repo_paths):
    results = {}
    for path in repo_paths:
        if not os.path.exists(path):
            print(f"Warning: Path {path} does not exist.")
            continue

        print(f"Analyzing repo at {path}...")
        # Simple analysis: count python files and lines of code
        try:
            find_proc = subprocess.run(["find", path, "-name", "*.py"], capture_output=True, text=True)
            py_files = find_proc.stdout.splitlines()

            line_count = 0
            if py_files:
                for f in py_files:
                    with open(f, 'rb') as fp:
                        line_count += sum(1 for _ in fp)

            results[path] = {
                "file_count": len(py_files),
                "line_count": line_count
            }
        except Exception as e:
            print(f"Error analyzing {path}: {e}")

    return results

def main():
    parser = argparse.ArgumentParser(description="Multi-repo source analysis")
    parser.add_argument("repos", nargs="+", help="Paths to repositories to analyze")
    args = parser.parse_args()

    analysis = analyze_repos(args.repos)
    print("\nRepo Analysis Summary:")
    for repo, data in analysis.items():
        print(f"{repo}: {data['file_count']} files, {data['line_count']} lines of code")

if __name__ == "__main__":
    main()
