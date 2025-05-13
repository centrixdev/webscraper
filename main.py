from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl # Added for Pydantic model and URL validation

from bs4 import BeautifulSoup
import requests

# Define a Pydantic model for the request body
class ScrapeItem(BaseModel):
    url: HttpUrl # Use HttpUrl for automatic URL validation

app = FastAPI(
    title="Web Scraper API",
    description="An API for extracting content from websites using BeautifulSoup", # Corrected library name
    version="1.0.0",
)

@app.post("/scrape/")
async def scrape_body(item: ScrapeItem): # Use the Pydantic model for request body
    """
    Scrape the body of a webpage and return its content.
    """
    try:
        # getting response object
        res = requests.get(str(item.url), allow_redirects=True) # Allow redirects to handle 301 responses
        res.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching URL: {e}")
    
    # Initialize the object with the document
    soup = BeautifulSoup(res.content, "html.parser")
    
    # Get the whole body tag
    tag = soup.body
    
    if not tag:
        raise HTTPException(status_code=404, detail="No body tag found in the webpage")
        
    # Collect strings from the body
    body_strings = [string for string in tag.strings if string.strip()]
    
    # Join the list of strings into a single string
    full_body_text = " ".join(body_strings)
        
    return {
        "success": True,
        "data": full_body_text
    }
   


@app.post("/scrape-links/")
async def scrape_links(item: ScrapeItem): # Use the Pydantic model for request body
    """
    Scrape a webpage and return all unique internal links.
    """
    try:
        # Convert HttpUrl to string for requests
        res = requests.get(str(item.url), allow_redirects=True) # Allow redirects to handle 301 responses
        res.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching URL: {e}")
    
    # Initialize the object with the document
    soup = BeautifulSoup(res.content, "html.parser")
    
    internal_links = set() # Use a set to store unique links to avoid duplicates
    
    # Parse the input URL to get its scheme and netloc (e.g., "http://example.com")
    # This will be used to identify if a link is internal.
    # str(item.url) is used because item.url is a Pydantic HttpUrl object.
    parsed_input_url = requests.utils.urlparse(str(item.url))
    base_domain = f"{parsed_input_url.scheme}://{parsed_input_url.netloc}"

    for a_tag in soup.find_all("a", href=True): # Find all <a> tags that have an href attribute
        href = a_tag["href"]
        
        # Resolve the href to an absolute URL. 
        # requests.compat.urljoin handles various cases like relative paths ("/about"), 
        # page-relative paths ("contact.html"), or full URLs.
        # str(item.url) serves as the base URL for resolving relative links.
        full_url = requests.compat.urljoin(str(item.url), href)
        
        # Check if the resolved full_url starts with the base_domain of the input URL.
        # This determines if the link is internal.
        if full_url.startswith(base_domain):
            internal_links.add(full_url)

    if not internal_links:
        return {
            "success": True,
            "message": "No internal links found on the webpage.",
            "data": []
        }
        
    return {
        "success": True,
        "data": sorted(list(internal_links)) # Return the unique links as a sorted list
    }

if __name__ == "__main__":
    import uvicorn
    # To run: uvicorn main:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
