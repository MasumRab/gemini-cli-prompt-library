from graphite_agent.bootstrap import build_executor


def main():
    build_executor(enable_post_action_verification=True).execute()


if __name__ == "__main__":
    main()
