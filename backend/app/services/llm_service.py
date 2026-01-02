import os
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
import google.generativeai as genai
from app.utils.summary_headline import build_summary_headline

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
        time_range: str = None,
        language: Optional[str] = None
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
        if language:
            print(f"[LLM SERVICE] Language: {language}")
        
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
        
        language_map = {
            "zh": "Chinese",
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "ja": "Japanese",
            "ko": "Korean",
            "pt": "Portuguese",
            "ru": "Russian",
            "it": "Italian",
            "ar": "Arabic",
            "hi": "Hindi",
            "id": "Indonesian",
            "tr": "Turkish",
            "vi": "Vietnamese",
            "th": "Thai",
            "nl": "Dutch"
        }
        language_label = language_map.get((language or "en").lower(), "English")

        # Create prompt - emphasize topics in the prompt rather than filtering
        if topics and len(topics) > 0:
            topics_str = ", ".join(topics)
            topics_instruction = f"""
You are an analytical assistant producing a high-signal X (Twitter) activity digest.

User interests:
{topics_str}

Primary goal:
Help the user quickly understand the dominant themes, key signals, and strategic implications in this account’s tweets, with clear prioritization based on the user’s interests.

Instructions:
- FIRST, infer the single dominant theme across all tweets and state it clearly.
- Use a pyramid principle structure: conclusion first, then supporting points.
- Treat user interest topics as the primary signal; everything else is secondary.
- Prominently feature tweets that explicitly mention these topics and explain why they matter.
- Include non-topic tweets ONLY if they provide strong context, signal amplification, or strategic contrast.
- Avoid chronological retelling or tweet-by-tweet summaries.
- Focus on insights, patterns, and implications rather than neutral description.
- Write concisely, analytically, and with clear prioritization.
"""
        else:
            topics_instruction = ""
            topics_str = "general topics"
        
        account_line = f"Account: @{x_username}\n" if x_username else ""
        time_line = f"Time range: {time_range}\n" if time_range else ""

        prompt = f"""Please provide a concise, insight-driven analysis of the following tweets from a user's X (Twitter) account.
Respond in {language_label}. Use plain text only: no markdown, no bullets, no asterisks.
First output a headline as:
Headline: <12-18 words, news-style, no dates or time ranges>
Then output:
Summary:
<2-3 short paragraphs>
{topics_instruction}
{account_line}{time_line}Tweets:
{combined_text}

Please structure the response as:
1. One-sentence executive summary stating the dominant theme or signal of this account’s activity during the time range.
2. Core insights related to the user's interest topics: {topics_str}, explaining what these tweets indicate or imply, with supporting evidence.
3. Secondary or non-topic content, briefly summarized and clearly deprioritized.

Guidelines:
- Lead with judgment, not description.
- Do not retell tweets; synthesize patterns and implications.
- Treat user-interest topics as primary signal and everything else as secondary context.

Make sure the analysis explicitly references the account and time range and is grounded in the tweets provided above.
Keep the summary concise (2–3 short paragraphs). If non-topic content dominates engagement but not strategic relevance, explicitly label it as high-engagement but low-signal.
"""

        
        print(f"[LLM SERVICE] Prompt length: {len(prompt)} characters")
        print(f"[LLM SERVICE] Making API call to {self.provider}...")

        try:
            if self.provider == "gemini":
                print("[LLM SERVICE] Using Gemini API...")
                response = self.model.generate_content(prompt)
                print(f"[LLM SERVICE] ✅ Gemini response received")
                print(f"[LLM SERVICE] Response type: {type(response)}")
                if hasattr(response, 'text'):
                    summary_text = response.text
                    usage = self._extract_gemini_usage(response)
                    headline, summary = self._extract_headline_and_summary(summary_text)
                    if not headline:
                        headline = build_summary_headline(summary)
                    print(f"[LLM SERVICE] Summary length: {len(summary)} characters")
                    print(f"[LLM SERVICE] Summary preview: {summary[:200]}...")
                    return {"summary": summary, "headline": headline, "usage": usage}
                else:
                    print(f"[LLM SERVICE] ⚠️  Response object structure: {dir(response)}")
                    raw_text = str(response)
                    headline, summary = self._extract_headline_and_summary(raw_text)
                    if not headline:
                        headline = build_summary_headline(summary)
                    return {"summary": summary, "headline": headline, "usage": {"input_tokens": 0, "output_tokens": 0}}
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
                raw_text = response.choices[0].message.content
                usage = {
                    "input_tokens": getattr(response.usage, "prompt_tokens", 0),
                    "output_tokens": getattr(response.usage, "completion_tokens", 0)
                }
                headline, summary = self._extract_headline_and_summary(raw_text)
                if not headline:
                    headline = build_summary_headline(summary)
                print(f"[LLM SERVICE] Summary length: {len(summary)} characters")
                return {"summary": summary, "headline": headline, "usage": usage}
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

    def _extract_headline_and_summary(self, text: str) -> Tuple[Optional[str], str]:
        if not text:
            return None, ""
        headline = None
        summary_lines = []
        lines = text.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.lower().startswith("headline:"):
                headline = line.split(":", 1)[1].strip()
            elif line.lower().startswith("summary:"):
                remainder = line.split(":", 1)[1].strip()
                if remainder:
                    summary_lines.append(remainder)
                summary_lines.extend(lines[i + 1 :])
                break
            i += 1
        if not summary_lines:
            return headline, text.strip()
        return headline, "\n".join(summary_lines).strip()
