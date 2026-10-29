"""Five-class coverage audit: locate each required token class with real line numbers."""
import os
ARM = os.path.dirname(os.path.abspath(__file__))
TARGETS = ["color", "spacing", "typography", "component state", "breakpoint"]
FILES = ["dashboard-design-system.md",
         os.path.join("design-system", "data-analytics-dashboard", "TOKENS.md"),
         os.path.join("design-system", "data-analytics-dashboard", "MASTER.md")]
def scan(rel, needle):
    path = os.path.join(ARM, rel)
    hits = []
    with open(path, encoding="utf-8") as fh:
        for i, ln in enumerate(fh, start=1):
            if needle in ln.lower():
                hits.append(i)
    return hits[:6]
def main():
    for rel in FILES:
        print("### " + rel)
        for needle in TARGETS:
            print("   ", needle.ljust(16), "-> lines", scan(rel, needle))
    print("### _gen_stdout.txt RUN markers")
    print("   ", scan("_gen_stdout.txt", "run "))
if __name__ == "__main__":
    main()
