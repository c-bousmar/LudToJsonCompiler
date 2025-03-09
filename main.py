import sys
import src.fetch_lud_files as fetcher
import src.clean_files as cleaner
import src.parse_json as parser

def main(file="all"):
    if file == "all":
        fetcher.main()
        cleaner.main()
        parser.main()
    
    else:
        fetcher.main(file)

        cleaner.main(file)

        parser.main(file)

    print("\n✅ Process completed successfully!")

if __name__ == "__main__":
    args = sys.argv[1:]
    
    if len(args) > 1:
        print("❌ Incorrect usage.")
        print("Usage:")
        print("  python main.py          # Run the full pipeline normally")
        print("  python main.py <name>    # Run the full pipeline for a specific .lud file")
        sys.exit(1)

    if len(args) == 0:
        main()
    else:
        main(sys.argv[1])
