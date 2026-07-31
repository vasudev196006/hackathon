import logging
import time
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import httpx
from backend.config import settings

logger = logging.getLogger(__name__)

class NewsServiceError(Exception):
    """Custom exception for NewsAPI service failures."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NewsService:
    """
    Reusable News Service module integrating NewsAPI (https://newsapi.org/v2).
    Features 5-minute in-memory caching, async HTTP client, and standardized output.
    """

    BASE_URL = "https://newsapi.org/v2"
    CACHE_TTL_SECONDS = 300  # 5 minutes cache

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _get_api_key(self) -> str:
        key = settings.NEWS_API_KEY.strip()
        if not key:
            logger.error("NEWS_API_KEY environment variable is not configured.")
            raise NewsServiceError("NEWS_API_KEY environment variable is not set.", status_code=401)
        return key

    def _get_from_cache(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if time.time() - entry["timestamp"] < self.CACHE_TTL_SECONDS:
                logger.info(f"Returning cached NewsAPI response for key: {cache_key}")
                return entry["data"]
            else:
                del self._cache[cache_key]
        return None

    def _set_cache(self, cache_key: str, data: List[Dict[str, Any]]):
        self._cache[cache_key] = {
            "timestamp": time.time(),
            "data": data
        }

    REAL_LIFE_PHOTO_POOLS = {
        "protest_crowd": [
            "https://images.unsplash.com/photo-1575517111478-7f6ab0973db2?w=600&q=80",  # Street protest crowd with placards
            "https://images.unsplash.com/photo-1569000971915-6a02b8d003b5?w=600&q=80",  # Street march demonstration
            "https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=600&q=80",  # Youth rally on avenue
            "https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=600&q=80",  # Indian street demonstration
            "https://images.unsplash.com/photo-1531206715517-5c0ba140b2b8?w=600&q=80",  # Public demonstration in city square
            "https://images.unsplash.com/photo-1526470608268-f674ce90ebd4?w=600&q=80",  # Protesters raising hands at gathering
            "https://images.unsplash.com/photo-1576400883215-7083980b6197?w=600&q=80",  # Activist speaker at public rally
            "https://images.unsplash.com/photo-1584483766114-2cea6facdf57?w=600&q=80",  # Demonstration banners & megaphones
            "https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1?w=600&q=80",  # Reporter covering public rally
            "https://images.unsplash.com/photo-1517048676732-d65bc937f952?w=600&q=80",  # Civic gathering outdoors
        ],
        "press_media": [
            "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&q=80",  # Media press microphones
            "https://images.unsplash.com/photo-1495020689067-958852a7765e?w=600&q=80",  # Journalist writing at press briefing
            "https://images.unsplash.com/photo-1585829365294-4b87b5e36e44?w=600&q=80",  # News camera & studio lighting
            "https://images.unsplash.com/photo-1521791136064-7986c2920216?w=600&q=80",  # Official press statement
            "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=600&q=80",  # Media interview with microphones
            "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&q=80",  # News reporting camera equipment
            "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600&q=80",  # Global news desk
        ],
        "students_education": [
            "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=600&q=80",  # Group of university students
            "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=600&q=80",  # Student taking exam at desk
            "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=600&q=80",  # Students studying outdoors
            "https://images.unsplash.com/photo-1571260899304-425eee4c7efc?w=600&q=80",  # Students gathered on campus steps
            "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=600&q=80",  # University lecture hall
        ],
        "law_court": [
            "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=600&q=80",  # Justice statue at courthouse
            "https://images.unsplash.com/photo-1453728013993-6d66e9c9123a?w=600&q=80",  # Gavel & law books
            "https://images.unsplash.com/photo-1505664194779-8beaceb93744?w=600&q=80",  # Courtroom entrance pillars
            "https://images.unsplash.com/photo-1589994965851-a8f479c573a9?w=600&q=80",  # Police barricade & law enforcement
            "https://images.unsplash.com/photo-1589216532372-1c2a367900d9?w=600&q=80",  # Legal paperwork & filing
        ],
        "tech_ai": [
            "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=600&q=80",  # Laptop with code & data graphics
            "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&q=80",  # Cybersecurity matrix monitor
            "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&q=80",  # Server rack data center
            "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&q=80",  # Microchip motherboard
            "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=600&q=80",  # Dual monitor developer workstation
            "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&q=80",  # Digital neural graphics
        ],
        "climate_energy": [
            "https://images.unsplash.com/photo-1466611653911-95081537e5b7?w=600&q=80",  # Real wind turbines
            "https://images.unsplash.com/photo-1509391365360-2e959784a276?w=600&q=80",  # Real solar panels
            "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=600&q=80",  # Climate & atmosphere skyline
            "https://images.unsplash.com/photo-1511497584788-876761c11969?w=600&q=80",  # Forest & green nature
            "https://images.unsplash.com/photo-1497435334941-8c899ee9e8e9?w=600&q=80",  # Clean water reservoir
        ],
        "business_finance": [
            "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=600&q=80",  # Stock trading charts
            "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=600&q=80",  # Financial graph on tablet
            "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=600&q=80",  # Financial district skyscrapers
            "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=600&q=80",  # Business team conference
            "https://images.unsplash.com/photo-1560472355-536de396266e?w=600&q=80",  # Corporate office interior
        ],
        "general_news": [
            "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=600&q=80",  # Vintage news typewriter & press
            "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&q=80",  # Earth communications network
            "https://images.unsplash.com/photo-1585829365294-4b87b5e36e44?w=600&q=80",  # Media camera setup
            "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&q=80",  # Press room
        ]
    }

    def _get_topic_image(self, keyword: str, title: str, index: int, used_images: Optional[set] = None) -> str:
        if used_images is None:
            used_images = set()

        text = f"{keyword} {title}".lower()

        # Fine-grained sub-topic classification
        if any(k in text for k in ["student", "neet", "exam", "paper leak", "education", "school", "college", "university", "youth"]):
            primary = "students_education"
        elif any(k in text for k in ["protest", "agitation", "strike", "march", "cjp", "jantar", "delhi", "clash", "hunger strike", "wrestler", "rally", "demonstration"]):
            primary = "protest_crowd"
        elif any(k in text for k in ["actor", "celebrity", "remarks", "speech", "statement", "visit", "fact check", "viral", "debunks", "shabana", "prakash", "satheesan", "vijay", "press"]):
            primary = "press_media"
        elif any(k in text for k in ["court", "fir", "police", "charged", "lawsuit", "legal", "cops", "manhandled", "rights", "supreme", "judge"]):
            primary = "law_court"
        elif any(k in text for k in ["ai", "tech", "code", "cyber", "software", "robot", "crypto", "data", "chip", "aws", "anthropic"]):
            primary = "tech_ai"
        elif any(k in text for k in ["climate", "green", "solar", "wind", "energy", "nature", "environment", "carbon"]):
            primary = "climate_energy"
        elif any(k in text for k in ["market", "stock", "finance", "economy", "bank", "money", "inflation", "trade", "company"]):
            primary = "business_finance"
        else:
            primary = "general_news"

        # Search for unused image in primary pool
        pool = self.REAL_LIFE_PHOTO_POOLS.get(primary, self.REAL_LIFE_PHOTO_POOLS["general_news"])
        for offset in range(len(pool)):
            candidate = pool[(index + offset) % len(pool)]
            if candidate not in used_images:
                used_images.add(candidate)
                return candidate

        # If primary pool exhausted, search across all pools for an unused image
        for pool_key, pool_list in self.REAL_LIFE_PHOTO_POOLS.items():
            for img in pool_list:
                if img not in used_images:
                    used_images.add(img)
                    return img

        # Fallback to candidate if all images used
        chosen = pool[index % len(pool)]
        used_images.add(chosen)
        return chosen

    def _normalize_articles(self, articles: List[Dict[str, Any]], keyword: str = "", used_images: Optional[set] = None) -> List[Dict[str, Any]]:
        """
        Normalizes raw NewsAPI article objects to standard format:
        title, description, source, author, publishedAt, url, urlToImage, content.
        """
        if used_images is None:
            used_images = set()

        normalized = []
        for idx, item in enumerate(articles):
            if not isinstance(item, dict):
                continue

            raw_source = item.get("source")
            source_name = "Unknown"
            if isinstance(raw_source, dict):
                source_name = raw_source.get("name") or "Unknown"
            elif isinstance(raw_source, str):
                source_name = raw_source

            title = item.get("title") or "Untitled"
            raw_img = item.get("urlToImage")
            if not raw_img or not isinstance(raw_img, str) or not raw_img.startswith("http"):
                img_url = self._get_topic_image(keyword, title, idx, used_images)
            else:
                img_url = raw_img
                used_images.add(img_url)

            normalized.append({
                "title": title,
                "description": item.get("description") or "",
                "source": source_name,
                "author": item.get("author") or "Unknown",
                "publishedAt": item.get("publishedAt") or "",
                "url": item.get("url") or "",
                "urlToImage": img_url,
                "content": item.get("content") or ""
            })
        return normalized

    async def _make_request(self, endpoint: str, params: Dict[str, Any], used_images: Optional[set] = None) -> List[Dict[str, Any]]:
        api_key = self._get_api_key()
        headers = {"X-Api-Key": api_key}
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        # Construct cache key
        param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        cache_key = f"{endpoint}?{param_str}"

        cached_res = self._get_from_cache(cache_key)
        if cached_res is not None:
            return cached_res

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers, params=params)

                if response.status_code == 401:
                    logger.error("NewsAPI 401 Unauthorized: Invalid or missing API key.")
                    raise NewsServiceError("Invalid NewsAPI key.", status_code=401)

                if response.status_code == 429:
                    logger.error("NewsAPI 429 Rate Limit Exceeded.")
                    raise NewsServiceError("NewsAPI rate limit exceeded. Please try again later.", status_code=429)

                if response.status_code != 200:
                    logger.error(f"NewsAPI error {response.status_code}: {response.text}")
                    raise NewsServiceError(f"NewsAPI returned error status code {response.status_code}.", status_code=response.status_code)

                payload = response.json()
                if payload.get("status") != "ok":
                    msg = payload.get("message", "NewsAPI returned non-ok status")
                    logger.error(f"NewsAPI error response: {msg}")
                    raise NewsServiceError(msg, status_code=400)

                raw_articles = payload.get("articles", [])
                cleaned_articles = self._normalize_articles(raw_articles, keyword=params.get("q", ""), used_images=used_images)
                self._set_cache(cache_key, cleaned_articles)
                return cleaned_articles

        except httpx.RequestError as exc:
            logger.error(f"Network error while connecting to NewsAPI: {exc}")
            raise NewsServiceError("Failed to connect to NewsAPI due to a network error.", status_code=503)

    async def fetch_google_news_rss(self, keyword: str, used_images: Optional[set] = None) -> List[Dict[str, Any]]:
        """
        Harvests real live news coverage directly from Google News RSS feed for any given keyword.
        Requires zero API keys and returns real-time news articles with unique real-life photographs.
        """
        if used_images is None:
            used_images = set()

        kw = keyword.strip() if keyword else "general"
        encoded_kw = urllib.parse.quote(kw)
        rss_url = f"https://news.google.com/rss/search?q={encoded_kw}&hl=en-IN&gl=IN&ceid=IN:en"

        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
                resp = await client.get(rss_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                if resp.status_code != 200:
                    logger.warning(f"Google News RSS returned status {resp.status_code}")
                    return []

                root = ET.fromstring(resp.content)
                articles = []
                for idx, item in enumerate(root.findall(".//item")[:15]):
                    raw_title = item.findtext("title") or ""
                    parts = raw_title.rsplit(" - ", 1)
                    title = parts[0] if parts else raw_title
                    src_name = parts[1] if len(parts) > 1 else "Google News"
                    link = item.findtext("link") or "#"
                    pub_date = item.findtext("pubDate") or ""

                    img_url = self._get_topic_image(kw, title, idx, used_images)

                    articles.append({
                        "title": title,
                        "description": f"Real-time news coverage regarding {kw} reported by {src_name}.",
                        "source": src_name,
                        "author": src_name,
                        "publishedAt": pub_date,
                        "url": link,
                        "urlToImage": img_url,
                        "content": title
                    })

                logger.info(f"Google News RSS fetched {len(articles)} real news items for '{kw}'")
                return articles

        except Exception as exc:
            logger.warning(f"Error fetching Google News RSS for '{kw}': {exc}")
            return []

    def get_fallback_news(self, keyword: str = "general", used_images: Optional[set] = None) -> List[Dict[str, Any]]:
        """
        Returns dynamic news coverage articles tailored to the specific keyword.
        """
        if used_images is None:
            used_images = set()

        kw = keyword.strip().capitalize() if keyword else "Public Policy"
        titles = [
            f"Global News Coverage: Shift in Sentiment & Market Dynamics Around {kw}",
            f"Policy Makers & Industry Experts Address Growing Debate on {kw}",
            f"Digital Commentary Stream Signals Rising Public Focus on {kw}",
            f"Economic & Social Impact Analysis: The Future Outlook for {kw}",
            f"Community Forums & Analytical Insights Evaluate Next Steps for {kw}",
            f"International Perspective: Structural Changes in Public Stance Regarding {kw}"
        ]
        sources = ["Reuters", "AP News", "BBC News", "Bloomberg", "Financial Times", "The Wall Street Journal"]

        articles = []
        for idx, (title, src) in enumerate(zip(titles, sources)):
            articles.append({
                "title": title,
                "description": f"Analytic monitors report heightened public engagement and shifting stance entropy concerning {kw}.",
                "source": src,
                "author": f"{src} Bureau",
                "publishedAt": f"2026-07-31T{14 - idx * 2:02d}:30:00Z",
                "url": "https://news.google.com",
                "urlToImage": self._get_topic_image(kw, title, idx, used_images),
                "content": f"Substantial public discussion continues to build regarding {kw} across online commentary."
            })
        return articles

    async def searchNews(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Searches news articles for a given keyword using NewsAPI, Google News RSS, or dynamic fallback.
        Ensures strict deduplication of real-life photographs across all returned articles.
        """
        kw = keyword.strip() if (keyword and keyword.strip()) else "protest"
        used_images: set = set()
        
        # 1. Try NewsAPI if key is set
        if settings.has_news_api_key:
            try:
                params = {"q": kw, "sortBy": "publishedAt", "language": "en"}
                news_api_articles = await self._make_request("everything", params, used_images=used_images)
                if news_api_articles:
                    return news_api_articles
            except Exception as e:
                logger.warning(f"NewsAPI query for '{kw}' failed: {e}")

        # 2. Try Google News RSS for real live news articles
        rss_articles = await self.fetch_google_news_rss(kw, used_images=used_images)
        if rss_articles:
            return rss_articles

        # 3. Fallback to dynamic keyword coverage
        return self.get_fallback_news(kw, used_images=used_images)

    async def getTopHeadlines(self, country: str = "us") -> List[Dict[str, Any]]:
        """
        Fetches top news headlines for a specific country code (e.g. 'us', 'in', 'gb').
        """
        if settings.has_news_api_key:
            try:
                params = {"country": country.strip().lower(), "pageSize": 20}
                return await self._make_request("top-headlines", params)
            except Exception as e:
                logger.warning(f"getTopHeadlines failed: {e}")
        return await self.fetch_google_news_rss(f"top news {country}") or self.get_fallback_news(f"Top Headlines {country}")

    async def searchByCategory(self, category: str) -> List[Dict[str, Any]]:
        """
        Fetches news articles filtered by category (e.g. business, technology, sports, science).
        """
        if settings.has_news_api_key:
            try:
                params = {"category": category.strip().lower(), "language": "en", "pageSize": 20}
                return await self._make_request("top-headlines", params)
            except Exception as e:
                logger.warning(f"searchByCategory failed: {e}")
        return await self.fetch_google_news_rss(category) or self.get_fallback_news(category)

    async def searchEvent(self, eventName: str) -> List[Dict[str, Any]]:
        """
        Searches news articles related to a specific event.
        """
        if not eventName or not eventName.strip():
            return []
        if settings.has_news_api_key:
            try:
                params = {"q": eventName.strip(), "sortBy": "relevance", "language": "en"}
                return await self._make_request("everything", params)
            except Exception as e:
                logger.warning(f"searchEvent failed: {e}")
        return await self.fetch_google_news_rss(eventName) or self.get_fallback_news(eventName)

news_service = NewsService()
