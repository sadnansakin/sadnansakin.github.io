import requests

# Making a GET request to retrieve the content of a web page
response = requests.get("https://www.example.com")
print("Response code:", response.status_code)
print("Response content:", response.text[:100], "...")

# Making a POST request to submit data to a web page
data = {"username": "john", "password": "secret"}
response = requests.post("https://www.example.com/login", data=data)
print("Response code:", response.status_code)
print("Response content:", response.text[:100], "...")

# Making a request with query parameters
response = requests.get("https://www.example.com/search", params={"q": "requests module"})
print("Response code:", response.status_code)
print("Response content:", response.text[:100], "...")

# Making a request with headers
headers = {"User-Agent": "MyUserAgent/1.0"}
response = requests.get("https://www.example.com", headers=headers)
print("Response code:", response.status_code)
print("Response content:", response.text[:100], "...")

# Making a request to retrieve a binary file
response = requests.get("https://www.example.com/image.jpg")
open("image.jpg", "wb").write(response.content)
