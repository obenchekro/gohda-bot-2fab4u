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