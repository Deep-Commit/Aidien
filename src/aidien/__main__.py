import argparse
import logging
from aidien.core import Aidien

def main():
    parser = argparse.ArgumentParser(
        prog="aidien",
        description="A CLI tool to embed files and process queries over your code base."
    )
    parser.add_argument(
        "--env",
        type=str,
        help="Path to .env file"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="The query to process (e.g., 'Add doc strings to all the functions explaining what they do.')"
    )
    parser.add_argument(
        "--directory",
        type=str,
        help="Directory to scan for code files"
    )
    args = parser.parse_args()

    # Initialize Aidien with optional env file
    aidien = Aidien(env_path=args.env)

    # Embed directory if specified
    if args.directory:
        aidien.embed_directory(args.directory)
    
    # Process query if provided
    if args.query:
        aidien.process_query(args.query)

if __name__ == "__main__":
    main() 