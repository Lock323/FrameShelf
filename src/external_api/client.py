from external_api.http_client import HTTPClient, ImageHTTPClient

tmdb_client = HTTPClient(base_url="https://api.themoviedb.org")

image_tmdb_client = ImageHTTPClient(base_url="https://image.tmdb.org")