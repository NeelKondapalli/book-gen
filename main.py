import argparse
from modules.ingestion import Ingestor
import chromadb

def ingest(dir_path, name):
    directory_ingestor = Ingestor(dir_path, name)
    print(f"\n\nIngesting documents in: {dir_path} and name {name}\n\n")
    directory_ingestor.process_directory()


def test_query(name, query):

    client = chromadb.PersistentClient()
    try:
        collection = client.get_collection(name=name)
    except:
        raise Exception(f"Collection of name {name} does not exist")
    
    results = collection.query(
        query_texts=[query],
        n_results=7 
    )

    print("\n\n")
    print(results)
    print("\n\n")




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


    args = parser.parse_args()


    if not args.command:
        parser.print_help()
        return

    if args.command == "ingest":
        ingest(args.dir, args.name)

    if args.command == "test_query":
        test_query(args.name, args.query)


if __name__ == "__main__":
    main()
