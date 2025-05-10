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
        res = requests.get(str(item.url)) # Convert HttpUrl to string for requests
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
    body_strings = [string for string in tag.strings]
        
    return {
        "success": True,
        "data": body_strings
    }
   


if __name__ == "__main__":
    import uvicorn
    # To run: uvicorn main:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
