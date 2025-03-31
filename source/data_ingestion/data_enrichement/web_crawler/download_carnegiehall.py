import requests
import os
import json
import time
import random
from pathlib import Path
from queue import Queue
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

global_headers = {
    "Accept": "application/sparql-results+json,*/*;q=0.9",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/132.0.0.0 Safari/537.36"
}
global_cookies = {}


def fetch_event_urls(endpoint):
    """Fetch all event URLs from SPARQL endpoint"""
    query = """
    PREFIX schema: <http://schema.org/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?event
    WHERE {
      ?event a schema:Event ;
             schema:organizer ?organizer .
      ?organizer rdfs:label ?label .
      FILTER(CONTAINS(?label, "New York Philharmonic"))
    }
    ORDER BY ?event
    """
    data = {"query": query}
    response = requests.post(
        endpoint, headers=global_headers, cookies=global_cookies, data=data)
    if response.status_code == 200:
        json_data = response.json()
        return [binding["event"]["value"] for binding in json_data["results"]["bindings"]]
    else:
        print(f"Failed to fetch event URLs: {response.status_code}")
        return []


def merge_turtle_files():
    """Merge all .ttl files into single output"""
    output_file = "data/00_all.ttl"
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for file in sorted(Path("data").glob("*.ttl")):
            with open(file, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read() + "\n")
    print("All Turtle files merged into all.ttl")


def save_event_data(event_url):
    turtle_url = f"{event_url}/turtle"
    filename = f"data/{event_url.split('/')[-1]}.ttl"

    if Path(filename).exists():
        print(f"Skipping existing file: {filename}")
        return

    print(f"Downloading: {turtle_url}")
    response = requests.get(
        turtle_url, headers=global_headers, cookies=global_cookies)
    if response.status_code == 200:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Saved: {filename}")
    else:
        print(f"Download failed {turtle_url}: {response.status_code}")


def worker(queue):
    while not queue.empty():
        event_url = queue.get()
        save_event_data(event_url)
        queue.task_done()


def main():
    endpoint = "https://data.carnegiehall.org/sparql/"
    num_workers = 50
    Path("data").mkdir(exist_ok=True)
    event_urls = fetch_event_urls(endpoint)
    random.shuffle(event_urls)

    queue = Queue()
    for event_url in event_urls:
        queue.put(event_url)

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        for _ in range(num_workers):
            executor.submit(worker, queue)

    queue.join()
    print("Data crawling completed")
    merge_turtle_files()


if __name__ == "__main__":
    # Query the Carnegie Hall SPARQL endpoint using filter Venue == "New York Philharmonic"
    # And after feched a list of event urls, download the turtle files for each event
    # Finally, merge all turtle files into a single file
    main()
