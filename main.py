import argparse
from ingest.ingestion import Ingestor
from generate.generation import Generator
import chromadb

def ingest(dir_path, name):
    directory_ingestor = Ingestor(dir_path, name)
    directory_ingestor.process_directory()


def test_query(name, query):

    client = chromadb.PersistentClient()
    try:
        collection = client.get_collection(name=name)
    except:
        raise Exception(f"Collection of name {name} does not exist")
    
    results = collection.query(
        query_texts=[query],
        n_results=7,
        include = ["documents"]
    )

    print("\n\n" + results + "\n\n")

def generate(prompt, name):
    client = chromadb.PersistentClient()
    try:
        collection = client.get_collection(name=name)
    except:
        raise Exception(f"Collection of name {name} does not exist")
    generator = Generator(prompt, name)
    generator.generate()




def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", help="Run a command")
    


    process_parser = subparsers.add_parser("ingest", help="Ingest documents in a directory")
    process_parser.add_argument(
        "--dir",
        required=True,
        help="Directory path to process."
    )

    process_parser.add_argument(
        "--name",
        required=True,
        help="Document collection name."
    )

    process_parser = subparsers.add_parser("test_query", help="Test a query on Chroma")
    process_parser.add_argument(
        "--name",
        required=True,
        help="Document collection name."
    )
    process_parser.add_argument(
        "--query",
        required=True,
        help="Document query"
    )

    process_parser = subparsers.add_parser("generate", help="Test a query on Chroma")
    process_parser.add_argument(
        "--name",
        required=True,
        help="Document collection name."
    )
    process_parser.add_argument(
        "--prompt",
        required=True,
        help="Prompt for generation."
    )


    args = parser.parse_args()


    if not args.command:
        parser.print_help()
        return

    if args.command == "ingest":
        ingest(args.dir, args.name)

    if args.command == "test_query":
        test_query(args.name, args.query)
    
    if args.command == "generate":
        generate(args.prompt, args.name)


if __name__ == "__main__":
    main()
