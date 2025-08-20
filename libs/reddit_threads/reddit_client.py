import praw

class RedditVNTLFetcher:
    def __init__(self, client_id, client_secret, username="Humble_Informant6429", keyword="Translation & Release Status Update/Discussion"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.keyword = keyword

        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            username=self.username,
            user_agent=f'myredditapp/0.1 by {self.username}'
        )

    def fetch_vnts_posts(self, logger=None):
        try:
            user = self.reddit.redditor(self.username)
            if logger:
                logger.info(f"Fetching posts from Reddit user {self.username}...")
            posts = []
            for submission in user.submissions.new(limit=100):
                if logger:
                    logger.info(f"Checking post: {submission.title}")
                if self.keyword.lower() in submission.title.lower():
                    posts.append((submission.title, submission.url))
                    if logger:
                        logger.info(f"Found {len(posts)} relevant posts.")
            return posts
        except Exception as e:
            if logger:
                logger.error(f"Error fetching posts: {e}")
            return []

    def fetch_latest_vnts_post(self, logger=None):
        try:
            posts = self.fetch_vnts_posts()
            if posts:
                latest_post = posts[0]
                if logger:
                    logger.info(f"Latest VNTS post: {latest_post[0]} - {latest_post[1]}")
                return latest_post[1]
            else:
                if logger:
                    logger.warning("No VNTS posts found.")
                return None
        except Exception as e:
            if logger:
                logger.error(f"Error fetching latest post: {e}")
            return None

    def fetch_post_content(self, url, logger=None):
        try:
            submission = self.reddit.submission(url=url)
            author = submission.author.name if submission.author else "Unknown"
            if logger:
                logger.info(f"Fetching content from post: {submission.title} by {author}")
            post_content = submission.selftext
            if logger:
                logger.info("Post content fetched successfully.")
            return post_content
        except Exception as e:
            if logger:
                logger.error(f"Error fetching post content: {e}")
            return None
        
    def __fetch_reddit_posts_by_keywords(self, subreddits, keywords, limit=50, logger=None):
        results = []
        try:
            for sub in subreddits:
                subreddit = self.reddit.subreddit(sub)
                if logger:
                    logger.info(f"Scanning subreddit: {sub}")
                for post in subreddit.new(limit=limit):
                    title_lower = post.title.lower()
                    if any(k in title_lower for k in keywords):
                        results.append({
                            "title": post.title,
                            "url": post.url,
                            "subreddit": sub,
                            "timestamp": post.created_utc
                        })
                        if logger:
                            logger.info(f"Matching post found: {post.title} ({post.url})")
        except Exception as e:
            if logger:
                logger.error(f"Error fetching posts: {e}")
        return results
    
    def fetch_csgo_news_and_tradesites(self, logger=None, limit=300):
        subreddits = ["GlobalOffensive", "cs2", "csgo", "GlobalOffensiveTrade"]
        keywords = [
            "new skin", "skins", "cs2 skin", "csgo skin",
            "trusted site", "legit trading site", "safe trading",
            "cs2 trade", "csgo trade"
        ]
        return self.__fetch_reddit_posts_by_keywords(subreddits, keywords, limit=limit, logger=logger)

    def fetch_latest_game_releases(self, subreddits=None, keywords=None, limit=50, logger=None):
        if subreddits is None:
            subreddits = [
                "gaming", "games", "ps5", "XboxSeriesX", "pcgaming",
                "NintendoSwitch", "JRPG", "WesternRPG", "indiegames",
                "shmups", "gamecollecting", "Kojima"
            ]
        if keywords is None:
            keywords = [
                "release", "out now", "new game", "launch", "platformer",
                "jrpg", "western rpg", "shoot 'em up", "kojima",
                "action rpg", "metroidvania", "roguelike", "fps", "tactical rpg"
            ]
        return self.__fetch_reddit_posts_by_keywords(subreddits, keywords, limit=limit, logger=logger)
    
    def fetch_latest_ln_wn_news(self, subreddits=None, keywords=None, limit=50, logger=None):
        subreddits = ["LightNovels", "NovelTranslations", "webnovels"]
        keywords = ["release", "out now", "release date", "volume", "chapter", "announcement"]
        return self.__fetch_reddit_posts_by_keywords(subreddits, keywords, limit=limit, logger=logger)

    def fetch_crypto_news(self, subreddits=None, keywords=None, limit=50, logger=None):
        subreddits = ["CryptoCurrency", "Bitcoin", "ethereum", "CryptoMarkets"]
        keywords = ["bitcoin", "ethereum", "btc", "eth", "crypto", "bullish", "bearish", "pump", "crash", "halving"]
        return self.__fetch_reddit_posts_by_keywords(subreddits, keywords, limit=limit, logger=logger)

    def fetch_etf_news(self, subreddits=None, keywords=None, limit=50, logger=None):
        subreddits = ["investing", "ETFs", "financialindependence"]
        keywords = ["etf", "spy", "qqq", "vti", "vanguard", "blackrock", "dividend", "expense ratio"]
        return self.__fetch_reddit_posts_by_keywords(subreddits, keywords, limit=limit, logger=logger)

    def fetch_stock_market_news(self, subreddits=None, keywords=None, limit=50, logger=None):
        subreddits = ["stocks", "wallstreetbets", "europeanstocks", "francefinance"]
        keywords = ["cac 40", "s&p 500", "sp500", "nasdaq", "bull market", "buy", "sell", "stock alert", "earning report"]
        return self.__fetch_reddit_posts_by_keywords(subreddits, keywords, limit=limit, logger=logger)

    def fetch_when_to_buy_threads(self, subreddits=None, keywords=None, limit=50, logger=None):
        subreddits = ["stocks", "CryptoCurrency", "investing"]
        keywords = ["should I buy", "when to buy", "is it too late", "sell now", "entry point", "good time", "technical analysis"]
        return self.__fetch_reddit_posts_by_keywords(subreddits, keywords, limit=limit, logger=logger)