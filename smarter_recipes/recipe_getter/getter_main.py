import getter_bb
import getter_redbowls

def main():
    getter_bb.ingest_yaml('budget_bytes')
    getter_redbowls.open_recipes()

if __name__ == "__main__":
    main()

