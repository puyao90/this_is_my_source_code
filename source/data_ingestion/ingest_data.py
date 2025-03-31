from process_program import *
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Dict
import threading
from tqdm import tqdm
import os
from pathlib import Path
from operator import itemgetter


def init_graph() -> Graph:
    """Initialize RDF graph with bound namespaces"""
    graph = Graph()
    graph.bind("ex", EX)
    graph.bind("exdata", EXDATA)
    # graph.bind("wikidata", WIKIDATA)
    return graph
# ================== Data Loading and Export ==================


def load_programs(file_path: str) -> list:
    """Load and validate JSON program data"""
    programs = []

    if os.path.isdir(file_path):
        for filename in os.listdir(file_path):
            if filename.endswith(".json"):
                with open(os.path.join(file_path, filename), "r") as f:
                    programs.extend(json.load(f).get("programs", []))
    elif os.path.isfile(file_path):
        with open(file_path, "r") as f:
            programs.extend(json.load(f).get("programs", []))
    return programs


def export_graph(g: Graph, output_path: str):
    """Serialize and export RDF graph"""
    with open(output_path, "w") as f:
        f.write(g.serialize(format="turtle"))


def export_chunk(g: Graph, chunk_id: int, output_dir: str):
    """Export a single chunk to the output directory"""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"chunk_{chunk_id:04d}.ttl")
    with open(output_path, "w") as f:
        f.write(g.serialize(format="turtle"))
    return output_path


def chunk_exists(chunk_id: int, output_dir: str) -> bool:
    """Check if a chunk file already exists"""
    return os.path.exists(os.path.join(output_dir, f"chunk_{chunk_id:04d}.ttl"))


def process_program_chunk(programs: List[dict], chunk_id: int, output_dir: str) -> None:
    """Process a chunk of programs and save directly to file"""
    # Skip if chunk already exists
    if chunk_exists(chunk_id, output_dir):
        print(f"Chunk {chunk_id} already exists, skipping...")
        return None, chunk_id

    chunk_graph = init_graph()
    for program in programs:
        process_program(chunk_graph, program)

    # Export chunk immediately
    export_chunk(chunk_graph, chunk_id, output_dir)
    return chunk_graph, chunk_id


def merge_graphs(graphs: List[Graph]) -> Graph:
    """Merge multiple graphs into one"""
    final_graph = init_graph()
    for g in graphs:
        for triple in g:
            final_graph.add(triple)
    return final_graph


def sort_programs_by_id(programs: List[Dict]) -> List[Dict]:
    return sorted(programs, key=lambda x: int(x.get('programID', 0)))


# ================== Main Function ==================
# The main function of the data pipeline,
# 1, It loads the JSON files from New York Philharmonic
# 2, It cleans the data using the DataFieldProcessor
# 3, It sorts the data by programID
# 4, It splits the data into chunks and processes them in parallel
# 5, The process includes creating an RDF graph, processing each program, link the data by using the code of Data enrichment
# 6, Finally, it saves the processed data into Turtle files in the specified output directory
if __name__ == "__main__":
    # Initialize parameters
    json_folder_path = "/Users/sphy/workspace/CM3070/cm3070/src/data_source/json"
    output_dir = "chunks"  # Directory to store chunk files
    chunk_size = 100
    chunk_size = 10
    max_workers = 8  # Number of threads to use

    # Load, clean and sort programs
    raw_programs = load_programs(json_folder_path)
    cleaned_programs = DataFieldProcessor().clean([], raw_programs)
    sorted_programs = sort_programs_by_id(cleaned_programs)
    print(f"Loaded {len(sorted_programs)} programs.")

    # Split programs into chunks
    chunks = [
        sorted_programs[i:i + chunk_size]
        for i in range(0, len(sorted_programs), chunk_size)
    ]

    print(
        f"Processing {len(sorted_programs)} programs in {len(chunks)} chunks...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all chunks for processing
        future_to_chunk = {
            executor.submit(process_program_chunk, chunk, i, output_dir): i
            for i, chunk in enumerate(chunks)
        }

        # Process completed chunks with progress bar
        with tqdm(total=len(chunks), desc="Processing chunks") as pbar:
            for future in as_completed(future_to_chunk):
                chunk_id = future_to_chunk[future]
                try:
                    _, _ = future.result()
                    pbar.update(1)
                except Exception as e:
                    raise e
                    print(f"Chunk {chunk_id} generated an exception: {e}")

    print(f"Processing complete! Chunks saved to {output_dir}/")
