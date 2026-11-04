from graphite_agent.bootstrap import build_triage


def main():
    t = build_triage()
    t.print_summary()
    t.print_packets()


if __name__ == "__main__":
    main()
