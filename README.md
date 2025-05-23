

## Source Code Of Ⲥ𝙈Ȝ𝟘𝟟𝟘 Final Project: A Linked Data Approach to the Philharmonic’s Archives 
Auther: Yao Pu


# Data Processing Pipeline

A Python-based data processing pipeline for converting and enriching musical program data into linked RDF data.

## Project Structure

```
source/
├── __init__.py  
├── data_ingestion/          # Core data ingestion and processing  
│   ├── __init__.py  
│   ├── constants.py         # Shared constants and configurations  
│   ├── ingest_data.py       # Main ingestion pipeline  
│   ├── process_*.py         # Individual entity processors  
│   ├── utils.py             # Shared utilities  
│   ├── data_cleaning/       # Data cleaning components  
│   │   ├── __init__.py  
│   │   ├── abstract.py      # Abstract base classes  
│   │   ├── data_cleaner.py  # Data cleaning implementation  
│   │   └── utils.py         # Cleaning utilities  
│   └── data_enrichement/    # Data enrichment components  
│       ├── __init__.py  
│       ├── extra_api/       # External API integrations  
│       └── web_crawler/     # Web scraping utilities  
├── data_server/             # Data serving application  
│   ├── db.sqlite3           # SQLite database  
│   ├── manage.py            # Django management script  
│   └── linkeddata/          # Django app for linked data  
├── data_source/             # Source data analysis  
│   └── source_analysis/     # Data analysis tools  
└── rdf_output/              # Output directory for RDF data  
    ├── full_linked.ttl.zip  # <=========== Unzip to access 2M rows of linked data ===========>  
    ├── queries.txt          # Query notes  
    └── sample_linked.ttl    # Sample linked program to show structure and format  
```

## Key Components

- **Data Ingestion**: Handles loading and processing of JSON program data
- **Data Cleaning**: Cleanses and normalizes raw data
- **Data Enrichment**: Enhances data with external sources
- **Data Server**: Serves processed data via web interface
- **Source Analysis**: Tools for analyzing source data structure

## Main Features

- Parallel processing of data chunks
- RDF graph generation
- Data validation and cleaning
- Web crawling for data enrichment
- Output in Turtle format (.ttl)

## Usage

The main ingestion pipeline can be run through:

```sh
python source/data_ingestion/ingest_data.py
```


The django server app: Linked Data

Load full_linked.ttl to GraphDB first
Update GraphDB connection in linkeddata/model.py file based on your own environment

```
python manage.py runserver


Django version 5.1.7, using settings 'linkeddata.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```


