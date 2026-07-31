import urllib.request
import json

def test_news_images(query):
    url = f"http://localhost:8000/news?q={urllib.parse.quote(query)}"
    try:
        req = urllib.request.urlopen(url)
        articles = json.loads(req.read().decode())
        print(f"\n=== NEWS IMAGES FOR TOPIC: '{query}' ({len(articles)} articles) ===")
        images = [a.get("urlToImage") for a in articles]
        unique_images = set(images)
        print(f"Total Unique Images: {len(unique_images)} / {len(images)}")
        for idx, a in enumerate(articles[:5]):
            print(f"  [{idx+1}] {a.get('title')[:45]}...")
            print(f"      Image URL: {a.get('urlToImage')}")
    except Exception as e:
        print(f"Error testing news for '{query}': {e}")

if __name__ == "__main__":
    test_news_images("Artificial Intelligence")
    test_news_images("Climate Change & Renewable Energy")
    test_news_images("Protest & Civil Rights")
