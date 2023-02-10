import re

def extract_urls_from_js(js_file):
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', js_file)
    return urls

# Example usage:
js_code = """
var url1 = "https://www.
