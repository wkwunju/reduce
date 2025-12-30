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
    
    def summarize_tweets(
        self,
        tweets: List[Dict],
        topics: List[str] = None,
        x_username: str = None,
        time_range: str = None
    ) -> Dict:
        """
        Generate AI summary of tweets using Gemini or ChatGPT
        """
        print("=" * 80)
        print("[LLM SERVICE] Starting tweet summarization")
        print(f"[LLM SERVICE] Provider: {self.provider}")
        print(f"[LLM SERVICE] Number of tweets: {len(tweets)}")
        print(f"[LLM SERVICE] Topics: {topics if topics else 'None'}")
        if x_username:
            print(f"[LLM SERVICE] Username: @{x_username}")
        if time_range:
            print(f"[LLM SERVICE] Time range: {time_range}")
        
        if not tweets:
            print("[LLM SERVICE] ⚠️  No tweets to summarize")
            return {
                "summary": "No tweets found to summarize.",
                "usage": {"input_tokens": 0, "output_tokens": 0}
            }
        
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
You are an assistant that analyzes tweets for a user.

User interests:
{topics_str}

Instructions:
- Clearly separate content related to user interests vs. other content
- Prioritize tweets directly related to the user interests
- Prominently feature tweets that explicitly mention these topics
- Include other tweets only if they provide strong contextual or strategic relevance
- Focus on key insights, trends, and implications for the user
- Keep the summary concise and high-signal, write in pyramid principle format if possible
"""
        else:
            topics_instruction = ""
            topics_str = "general topics"
        
        account_line = f"Account: @{x_username}\n" if x_username else ""
        time_line = f"Time range: {time_range}\n" if time_range else ""

        prompt = f"""Please provide a concise analysis of the following tweets from a user's X (Twitter) account.
{topics_instruction}
{account_line}{time_line}Tweets:
{combined_text}

Please structure the response as:
1. A brief overview of this user's activity during the time range (who and when).
2. Core content related to the user's interest topics: {topics_str}.
3. Other notable content outside those topics.

Make sure the analysis explicitly references the account and time range and is grounded in the tweets provided above.

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
                    usage = self._extract_gemini_usage(response)
                    print(f"[LLM SERVICE] Summary length: {len(summary)} characters")
                    print(f"[LLM SERVICE] Summary preview: {summary[:200]}...")
                    return {"summary": summary, "usage": usage}
                else:
                    print(f"[LLM SERVICE] ⚠️  Response object structure: {dir(response)}")
                    return {"summary": str(response), "usage": {"input_tokens": 0, "output_tokens": 0}}
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
                usage = {
                    "input_tokens": getattr(response.usage, "prompt_tokens", 0),
                    "output_tokens": getattr(response.usage, "completion_tokens", 0)
                }
                print(f"[LLM SERVICE] Summary length: {len(summary)} characters")
                return {"summary": summary, "usage": usage}
        except Exception as e:
            error_msg = f"Error generating summary: {str(e)}"
            print(f"[LLM SERVICE] ❌ {error_msg}")
            print(f"[LLM SERVICE] Exception type: {type(e).__name__}")
            import traceback
            print(f"[LLM SERVICE] Traceback: {traceback.format_exc()}")
            return {"summary": error_msg, "usage": {"input_tokens": 0, "output_tokens": 0}}
        finally:
            print("=" * 80)

    def _extract_gemini_usage(self, response) -> Dict:
        usage = {"input_tokens": 0, "output_tokens": 0}
        usage_meta = getattr(response, "usage_metadata", None)
        if usage_meta:
            usage["input_tokens"] = getattr(usage_meta, "prompt_token_count", 0)
            usage["output_tokens"] = getattr(usage_meta, "candidates_token_count", 0)
        return usage
