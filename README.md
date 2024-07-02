## Mini Search Engine
This project implements a mini search engine with functionalities for crawling web pages, indexing content, and searching based on keyword proximity and frequency. It leverages various data structures such as hash tables and min-heaps to efficiently manage and retrieve data.


## Features
- **Harvests text content from HTML webpages**
- **Indexes words found on web pages along with their locations**
- **Finds all pages containing a specified keyword with the search method**
- **Identifies common pages containing two specified keywords and scores them based on proximity and frequency**
- **Retrieves the top search results**

## Data Structures
### Hash Table
- **A hash table (quadratic probing) is used to store and quickly retrieve keyword objects. It provides efficient insertions, deletions, and lookups, allowing the search engine to manage large volumes of indexed data**
### Min Heap
- **A min-heap is used to maintain and retrieve search results based on their scores. It allows efficient insertion and removal of elements, ensuring that the best search results are always accessible in logarithmic time**

## Usage
```python
if __name__ == "__main__":
    store = WebStore(HashQP)
# Url of the web page to search here:
    store.crawl("http://example.com", 2)

    while True:
# Words to search here
        term_one = input("Enter first term: ")
        term_two = input("Enter second term: ")
        store.search_pair(term_one, term_two)
        while True:
            try:
                result = store.get_result()
                print(result.site, round(result.score, 1))
            except IndexError:
                break
        print()
```
