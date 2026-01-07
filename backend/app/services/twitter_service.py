import requests
import os
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class TwitterService:
    def __init__(self):
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.base_url = os.getenv("TWITTER_API_BASE_URL", "https://api.twitterapi.io")
        if not self.api_key:
            raise ValueError("TWITTER_API_KEY not found in environment variables")
        
        # Rate limiting: Free tier allows 1 request per 5 seconds
        self.min_request_interval = 5.0  # seconds
        self.last_request_time = 0.0
        self.last_request_time = 0.0
    
    def get_user_tweets(
        self, 
        username: str, 
        since: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Fetch tweets from a specific user using twitterapi.io advanced search API
        Returns parsed tweet data with only important information
        """
        headers = {
            "X-API-Key": self.api_key
        }
        
        # Format times for the API query
        until_time = datetime.utcnow()
        if since:
            since_time = since
        else:
            # Default to last hour if no since time provided
            since_time = until_time - timedelta(hours=1)
        
        # Format times as strings in the format Twitter's API expects
        since_str = since_time.strftime("%Y-%m-%d_%H:%M:%S_UTC")
        until_str = until_time.strftime("%Y-%m-%d_%H:%M:%S_UTC")
        
        # Construct the advanced search query
        query = f"from:{username} since:{since_str} until:{until_str} include:nativeretweets"
        
        # API endpoint
        url = f"{self.base_url}/twitter/tweet/advanced_search"
        
        # Request parameters
        params = {
            "query": query,
            "queryType": "Latest"
        }
        
        print("=" * 80)
        print("[TWITTER API] Starting tweet fetch")
        print(f"[TWITTER API] Username: @{username}")
        print(f"[TWITTER API] Time range: {since_str} to {until_str}")
        print(f"[TWITTER API] URL: {url}")
        print(f"[TWITTER API] Query: {query}")
        print(f"[TWITTER API] Params: {params}")
        print(f"[TWITTER API] API Key present: {'Yes' if self.api_key else 'No'}")
        print("=" * 80)
        
        # Make the request and handle pagination
        # IMPORTANT: Limit pagination to reduce API calls and costs
        # Each page is a separate API call, so we limit to 1 page by default
        all_tweets = []
        next_cursor = None
        max_tweets = limit
        max_retries = 3
        max_pages = 1  # Limit to 1 page to minimize API calls (each page = 1 API call)
        page_count = 0
        
        try:
            while len(all_tweets) < max_tweets and page_count < max_pages:
                page_count += 1
                print(f"\n[TWITTER API] ===== Page {page_count} ===== ")
                print(f"[TWITTER API] Fetching page {page_count} for @{username}...")
                
                # Add cursor to params if we have one
                if next_cursor:
                    params["cursor"] = next_cursor
                    print(f"[TWITTER API] Using cursor for pagination: {next_cursor[:50]}...")
                
                # Rate limiting: ensure we wait at least 5 seconds between requests
                if page_count > 1:  # Only wait between pages, not before first request
                    self._wait_for_rate_limit()
                    print(f"[TWITTER API] Waiting 5 seconds before fetching next page (API rate limit)...")
                
                # Make request with retry logic
                response = None
                for attempt in range(max_retries):
                    try:
                        print(f"[TWITTER API] Making GET request (attempt {attempt + 1}/{max_retries})...")
                        response = requests.get(url, headers=headers, params=params, timeout=30)
                        
                        print(f"[TWITTER API] Response Status Code: {response.status_code}")
                        print(f"[TWITTER API] Response Headers: {dict(response.headers)}")
                        
                        # Handle rate limit (429)
                        if response.status_code == 429:
                            retry_after = self._get_retry_after(response)
                            wait_time = max(retry_after, self.min_request_interval)
                            print(f"[TWITTER API] ❌ Rate limit hit (429). Waiting {wait_time} seconds before retry...")
                            print(f"[TWITTER API] Response body: {response.text[:500]}")
                            time.sleep(wait_time)
                            self.last_request_time = time.time()
                            continue  # Retry the request
                        
                        response.raise_for_status()
                        print(f"[TWITTER API] ✅ Request successful (Status: {response.status_code})")
                        break  # Success, exit retry loop
                        
                    except requests.exceptions.RequestException as e:
                        print(f"[TWITTER API] ❌ Request exception: {str(e)}")
                        if hasattr(e, 'response') and e.response is not None:
                            print(f"[TWITTER API] Error response status: {e.response.status_code}")
                            print(f"[TWITTER API] Error response body: {e.response.text[:500]}")
                        if attempt == max_retries - 1:
                            raise  # Re-raise on final attempt
                        wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, 6s
                        print(f"[TWITTER API] Retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                
                if response is None:
                    raise Exception("Failed to get response after retries")
                
                print(f"[TWITTER API] Parsing JSON response...")
                data = response.json()
                print(f"[TWITTER API] Response keys: {list(data.keys())}")
                print(f"[TWITTER API] Has 'tweets' key: {'tweets' in data}")
                print(f"[TWITTER API] Has 'has_next_page' key: {'has_next_page' in data}")
                
                tweets = data.get("tweets", [])
                print(f"[TWITTER API] Raw tweets count from API: {len(tweets) if tweets else 0}")
                
                if not tweets:
                    print(f"[TWITTER API] ⚠️  No tweets in response. Full response structure:")
                    print(f"[TWITTER API] {str(data)[:1000]}")
                
                if tweets:
                    print(f"[TWITTER API] Processing {len(tweets)} raw tweets...")
                    # Parse and add tweets
                    parsed_count = 0
                    for idx, tweet in enumerate(tweets):
                        if idx < 3:  # Log first 3 tweets for debugging
                            print(f"[TWITTER API] Sample tweet {idx + 1} keys: {list(tweet.keys()) if isinstance(tweet, dict) else 'Not a dict'}")
                        parsed_tweet = self._parse_tweet(tweet)
                        if parsed_tweet:
                            if not parsed_tweet.get("username"):
                                parsed_tweet["username"] = username
                            all_tweets.append(parsed_tweet)
                            parsed_count += 1
                            if len(all_tweets) >= max_tweets:
                                break
                    print(f"[TWITTER API] Successfully parsed {parsed_count} tweets out of {len(tweets)} raw tweets")
                else:
                    print(f"[TWITTER API] ⚠️  No tweets to process")
                
                # Check if there are more pages - but don't fetch them to save API calls
                if data.get("has_next_page", False) and data.get("next_cursor", ""):
                    print(f"[API Call #{page_count}] More pages available, but limiting to {max_pages} page(s) to reduce API calls")
                    # Don't fetch more pages - we've limited to 1 page to minimize costs
                    break
                else:
                    break
            
            print("=" * 80)
            print(f"[TWITTER API] ✅ FINAL SUMMARY")
            print(f"[TWITTER API] Total tweets fetched: {len(all_tweets)}")
            print(f"[TWITTER API] API calls made: {page_count}")
            print(f"[TWITTER API] Username: @{username}")
            print("=" * 80)
            return all_tweets[:max_tweets]
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error fetching tweets for {username}: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" - Response: {e.response.text}"
                if e.response.status_code == 429:
                    error_msg = f"Rate limit exceeded. Please wait at least 5 seconds between requests. {error_msg}"
            print(error_msg)
            raise Exception(error_msg)
    
    def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limits"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last_request
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def _get_retry_after(self, response: requests.Response) -> float:
        """Extract retry-after time from response headers"""
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass
        return self.min_request_interval
    
    def _parse_tweet(self, tweet: Dict) -> Optional[Dict]:
        """
        Parse tweet data from twitterapi.io response and extract only important information:
        - text
        - likes
        - reposts/retweets
        - timestamp
        - tweet_id
        """
        try:
            if not isinstance(tweet, dict):
                print(f"[TWITTER API] ⚠️  Tweet is not a dict: {type(tweet)}")
                return None
            # Map twitterapi.io response fields to our standard format
            tweet_id = tweet.get("id") or tweet.get("tweetId") or tweet.get("id_str")
            text = tweet.get("text") or tweet.get("fullText") or tweet.get("content")
            created_at = tweet.get("createdAt") or tweet.get("created_at") or tweet.get("timestamp")
            
            # Extract engagement metrics
            likes = tweet.get("likeCount") or tweet.get("like_count") or tweet.get("favorite_count") or tweet.get("likes", 0)
            reposts = tweet.get("retweetCount") or tweet.get("retweet_count") or tweet.get("reposts", 0)
            
            # Build URL
            username = tweet.get("username") or tweet.get("user", {}).get("username", "")
            url = tweet.get("url") or tweet.get("tweetUrl")
            if not url and tweet_id:
                url = f"https://twitter.com/{username}/status/{tweet_id}" if username else f"https://twitter.com/i/web/status/{tweet_id}"
            
            parsed = {
                "tweet_id": tweet_id,
                "text": text,
                "likes": int(likes) if likes else 0,
                "reposts": int(reposts) if reposts else 0,
                "timestamp": created_at,
                "url": url
            }
            
            # Ensure we have at least text and timestamp
            if not parsed["text"] or not parsed["timestamp"]:
                print(f"[TWITTER API] ⚠️  Tweet missing required fields - text: {bool(parsed['text'])}, timestamp: {bool(parsed['timestamp'])}")
                return None
            
            return parsed
            
        except Exception as e:
            print(f"[TWITTER API] ❌ Error parsing tweet: {str(e)}")
            print(f"[TWITTER API] Tweet data type: {type(tweet)}")
            print(f"[TWITTER API] Tweet data (first 500 chars): {str(tweet)[:500]}")
            return None
    
    def filter_by_topics(self, tweets: List[Dict], topics: List[str]) -> List[Dict]:
        """
        Filter tweets by topics (keywords)
        """
        if not topics:
            return tweets
        
        filtered = []
        topics_lower = [topic.lower() for topic in topics]
        
        for tweet in tweets:
            text_lower = tweet.get("text", "").lower()
            if any(topic in text_lower for topic in topics_lower):
                filtered.append(tweet)
        
        return filtered
