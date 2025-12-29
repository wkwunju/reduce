import os
from typing import List, Dict
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class LLMService:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            # Use gemini-2.5-flash as default (latest and fastest)
            # Can be overridden with GEMINI_MODEL environment variable
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            print(f"[LLM SERVICE] Initializing Gemini with model: {model_name}")
            try:
                self.model = genai.GenerativeModel(model_name)
                self.provider = "gemini"
                print(f"[LLM SERVICE] ✅ Successfully initialized Gemini model: {model_name}")
            except Exception as e:
                print(f"[LLM SERVICE] ⚠️  Failed to initialize {model_name}, trying gemini-1.5-flash...")
                try:
                    self.model = genai.GenerativeModel("gemini-1.5-flash")
                    self.provider = "gemini"
                    print(f"[LLM SERVICE] ✅ Successfully initialized with fallback model: gemini-1.5-flash")
                except Exception as e2:
                    print(f"[LLM SERVICE] ❌ Failed to initialize any Gemini model: {str(e2)}")
                    raise
        elif self.openai_api_key:
            self.provider = "openai"
            # OpenAI would be imported here if needed
        else:
            raise ValueError("No LLM API key found. Set GEMINI_API_KEY or OPENAI_API_KEY")
    
    def summarize_tweets(self, tweets: List[Dict], topics: List[str] = None) -> str:
        """
        Generate AI summary of tweets using Gemini or ChatGPT
        """
        print("=" * 80)
        print("[LLM SERVICE] Starting tweet summarization")
        print(f"[LLM SERVICE] Provider: {self.provider}")
        print(f"[LLM SERVICE] Number of tweets: {len(tweets)}")
        print(f"[LLM SERVICE] Topics: {topics if topics else 'None'}")
        
        if not tweets:
            print("[LLM SERVICE] ⚠️  No tweets to summarize")
            return "No tweets found to summarize."
        
        # Prepare tweet content for LLM
        tweet_texts = []
        for idx, tweet in enumerate(tweets):
            tweet_str = f"Tweet: {tweet.get('text', '')}\n"
            tweet_str += f"Likes: {tweet.get('likes', 0)}, Reposts: {tweet.get('reposts', 0)}\n"
            tweet_str += f"Time: {tweet.get('timestamp', 'Unknown')}\n"
            tweet_texts.append(tweet_str)
            if idx < 2:  # Log first 2 tweets
                print(f"[LLM SERVICE] Sample tweet {idx + 1}: {tweet.get('text', '')[:100]}...")
        
        combined_text = "\n---\n".join(tweet_texts)
        print(f"[LLM SERVICE] Combined text length: {len(combined_text)} characters")
        
        # Create prompt - emphasize topics in the prompt rather than filtering
        if topics and len(topics) > 0:
            topics_str = ", ".join(topics)
            topics_instruction = f"""
IMPORTANT: The user is particularly interested in the following topics: {topics_str}

When summarizing, please:
- Give special attention to tweets that relate to these topics
- Highlight and emphasize content related to {topics_str}
- If tweets mention these topics, make sure to feature them prominently in your summary
- Even if a tweet doesn't directly mention these topics, include it if it's relevant or important
- Focus your summary on how the content relates to the user's interests: {topics_str}
"""
        else:
            topics_instruction = ""
            topics_str = "general topics"
        
        prompt = f"""Please provide a concise summary of the following tweets from a user's X (Twitter) account.
{topics_instruction}
Tweets:
{combined_text}

Please summarize:
1. Key themes and topics discussed (with special focus on the user's topics of interest if specified)
2. Notable engagement (likes, reposts) - especially for tweets related to the topics of interest
3. Important updates or announcements
4. Overall sentiment and trends
5. How the content relates to the user's topics of interest: {topics_str}

Keep the summary concise (2-3 paragraphs) and make sure to highlight content related to the user's topics of interest."""
        
        print(f"[LLM SERVICE] Prompt length: {len(prompt)} characters")
        print(f"[LLM SERVICE] Making API call to {self.provider}...")

        try:
            if self.provider == "gemini":
                print("[LLM SERVICE] Using Gemini API...")
                response = self.model.generate_content(prompt)
                print(f"[LLM SERVICE] ✅ Gemini response received")
                print(f"[LLM SERVICE] Response type: {type(response)}")
                if hasattr(response, 'text'):
                    summary = response.text
                    print(f"[LLM SERVICE] Summary length: {len(summary)} characters")
                    print(f"[LLM SERVICE] Summary preview: {summary[:200]}...")
                    return summary
                else:
                    print(f"[LLM SERVICE] ⚠️  Response object structure: {dir(response)}")
                    return str(response)
            elif self.provider == "openai":
                print("[LLM SERVICE] Using OpenAI API...")
                import openai
                openai.api_key = self.openai_api_key
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that summarizes social media content."},
                        {"role": "user", "content": prompt}
                    ]
                )
                print(f"[LLM SERVICE] ✅ OpenAI response received")
                summary = response.choices[0].message.content
                print(f"[LLM SERVICE] Summary length: {len(summary)} characters")
                return summary
        except Exception as e:
            error_msg = f"Error generating summary: {str(e)}"
            print(f"[LLM SERVICE] ❌ {error_msg}")
            print(f"[LLM SERVICE] Exception type: {type(e).__name__}")
            import traceback
            print(f"[LLM SERVICE] Traceback: {traceback.format_exc()}")
            return error_msg
        finally:
            print("=" * 80)

