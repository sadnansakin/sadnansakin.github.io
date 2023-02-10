import requests

def fetch_and_search(url, keyword):
    response = requests.get(url)
    content = response.content.decode("utf-8")
    if keyword in content:
        print(f"Keyword '{keyword}' found in the content of URL: {url}")
    else:
        print(f"Keyword '{keyword}' not found in the content of URL: {url}")

# Example usage:
fetch_and_search("https://www.example.com", "example")
