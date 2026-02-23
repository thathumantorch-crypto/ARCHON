"""
Web Scraper for ARCHON - Learning from AI Models and Conversations

This module provides web scraping capabilities to learn from:
- Popular AI model documentation
- Conversation examples and patterns
- Response templates and styles
- Current AI trends and best practices
"""

import requests
import re
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Iterable
from dataclasses import dataclass, asdict, is_dataclass
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs, quote_plus
from bs4 import BeautifulSoup
import logging

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScrapedContent:
    """Represents scraped content from web sources"""
    url: str
    title: str
    content: str
    content_type: str
    source: str
    timestamp: datetime
    relevance_score: float
    tags: List[str]
    metadata: Dict[str, Any]

class WebScraper:
    """Web scraper for learning from AI models and conversations"""
    
    SAFE_DOMAINS = {
        "platform.openai.com",
        "docs.anthropic.com",
        "ai.google.dev",
        "huggingface.co",
        "chatbotarena.com",
        "paperswithcode.com",
        "github.com",
        "youtube.com",
        "youtu.be",
    }
    REQUEST_TIMEOUT = 10
    RATE_LIMIT_SECONDS = 1.0

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.scraped_content = []
        self.ai_model_sources = self._load_ai_model_sources()
        self.conversation_sources = self._load_conversation_sources()
        self.learning_patterns = self._load_learning_patterns()
        self.humor_sources = self._load_humor_sources()
        self._last_request_ts = 0.0
        self.transcript_pause_seconds: float = 0.75

    def _respect_rate_limit(self):
        delta = time.time() - self._last_request_ts
        if delta < self.RATE_LIMIT_SECONDS:
            time.sleep(self.RATE_LIMIT_SECONDS - delta)
        self._last_request_ts = time.time()

    def _is_allowed_url(self, url: str) -> bool:
        try:
            domain = urlparse(url).netloc
            if domain.startswith("www."):
                domain = domain[4:]
            return domain in self.SAFE_DOMAINS
        except Exception:
            return False

    def _load_ai_model_sources(self) -> List[Dict[str, str]]:
        """Load AI model documentation sources"""
        return [
            {
                'name': 'OpenAI Documentation',
                'base_url': 'https://platform.openai.com/docs',
                'topics': ['conversation', 'responses', 'best-practices', 'api', 'examples']
            },
            {
                'name': 'Anthropic Documentation',
                'base_url': 'https://docs.anthropic.com/claude',
                'topics': ['conversation', 'responses', 'guidelines', 'examples']
            },
            {
                'name': 'Google AI Documentation',
                'base_url': 'https://ai.google.dev/docs',
                'topics': ['conversation', 'responses', 'models', 'examples']
            },
            {
                'name': 'Hugging Face Documentation',
                'base_url': 'https://huggingface.co/docs/transformers',
                'topics': ['conversation', 'models', 'examples', 'tutorials']
            }
        ]

    def _load_humor_sources(self) -> List[Dict[str, Any]]:
        """Curated humor/joke repositories from safelisted domains."""
        return [
            {
                'name': 'Official Joke API Repository',
                'url': 'https://github.com/15Dkatz/official_joke_api',
                'type': 'joke_repository',
                'tags': ['setup', 'punchline', 'api']
            },
            {
                'name': 'Joke Dataset Collection',
                'url': 'https://github.com/taivop/joke-dataset',
                'type': 'joke_dataset',
                'tags': ['dataset', 'standup', 'one-liners']
            },
            {
                'name': 'Awesome Comedy Resources',
                'url': 'https://github.com/seriousran/awesome-comedy',
                'type': 'reference_list',
                'tags': ['technique', 'writing', 'standup']
            },
        ]
    
    def _load_conversation_sources(self) -> List[Dict[str, str]]:
        """Load conversation example sources"""
        return [
            {
                'name': 'Chatbot Arena',
                'url': 'https://chatbotarena.com',
                'type': 'conversation_examples'
            },
            {
                'name': 'Papers with Code',
                'url': 'https://paperswithcode.com',
                'type': 'research_papers'
            },
            {
                'name': 'GitHub Discussions',
                'url': 'https://github.com',
                'type': 'code_discussions'
            }
        ]
    
    def _load_learning_patterns(self) -> Dict[str, List[str]]:
        """Load patterns to look for in scraped content"""
        return {
            'conversation_patterns': [
                r'hello.*?how.*?can.*?help',
                r'what.*?is.*?your.*?name',
                r'can.*?you.*?explain',
                r'how.*?do.*?i.*?start',
                r'tell.*?me.*?about',
                r'help.*?me.*?understand'
            ],
            'response_patterns': [
                r'i.*?can.*?help.*?you.*?with',
                r'let.*?me.*?explain',
                r'here.*?is.*?what.*?you.*?need.*?to.*?know',
                r'i.*?understand.*?you.*?want.*?to',
                r'based.*?on.*?my.*?knowledge',
                r'i.*?recommend.*?that.*?you'
            ],
            'technical_patterns': [
                r'algorithm.*?complexity',
                r'data.*?structure',
                r'machine.*?learning',
                r'neural.*?network',
                r'programming.*?language',
                r'api.*?integration'
            ]
        }
    
    def scrape_ai_documentation(self, source: Dict[str, str], max_pages: int = 5) -> List[ScrapedContent]:
        """Scrape AI model documentation"""
        scraped = []
        
        try:
            logger.info(f"Scraping {source['name']} documentation...")
            
            for topic in source['topics'][:max_pages]:
                url = f"{source['base_url']}/{topic}"

                if not self._is_allowed_url(url):
                    logger.warning(f"Skipping URL outside safelist: {url}")
                    continue

                try:
                    self._respect_rate_limit()
                    response = self.session.get(url, timeout=self.REQUEST_TIMEOUT)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract title
                    title = soup.find('title')
                    title_text = title.text.strip() if title else f"{source['name']} - {topic}"
                    
                    # Extract main content
                    content = self._extract_main_content(soup)
                    
                    # Calculate relevance
                    relevance = self._calculate_relevance(content, topic)
                    
                    scraped_content = ScrapedContent(
                        url=url,
                        title=title_text,
                        content=content,
                        content_type='documentation',
                        source=source['name'],
                        timestamp=datetime.now(),
                        relevance_score=relevance,
                        tags=[topic, 'ai', 'documentation'],
                        metadata={'source_type': 'ai_docs', 'topic': topic}
                    )
                    
                    scraped.append(scraped_content)
                    logger.info(f"Scraped: {title_text[:50]}...")
                    
                    # Rate limiting
                    time.sleep(1)
                    
                except requests.HTTPError as http_err:
                    logger.error(f"HTTP error scraping {url}: {http_err}")
                except Exception as e:
                    logger.error(f"Error scraping {url}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping {source['name']}: {e}")
        
        return scraped
    
    def scrape_conversation_examples(self, source: Dict[str, str], max_examples: int = 10) -> List[ScrapedContent]:
        """Scrape conversation examples"""
        scraped = []
        
        try:
            logger.info(f"Scraping conversation examples from {source['name']}...")

            if not self._is_allowed_url(source['url']):
                logger.warning(f"Skipping URL outside safelist: {source['url']}")
                return []

            self._respect_rate_limit()
            response = self.session.get(source['url'], timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for conversation patterns
            conversation_elements = self._find_conversation_elements(soup)
            
            for i, element in enumerate(conversation_elements[:max_examples]):
                content = element.get_text(strip=True)
                
                if len(content) > 50:  # Filter out very short content
                    scraped_content = ScrapedContent(
                        url=source['url'],
                        title=f"Conversation Example {i+1}",
                        content=content,
                        content_type='conversation',
                        source=source['name'],
                        timestamp=datetime.now(),
                        relevance_score=0.7,
                        tags=['conversation', 'example', source['type']],
                        metadata={'source_type': 'conversation', 'index': i}
                    )
                    
                    scraped.append(scraped_content)
                    
        except requests.HTTPError as http_err:
            logger.error(f"HTTP error scraping conversation examples from {source['name']}: {http_err}")
        except Exception as e:
            logger.error(f"Error scraping conversation examples from {source['name']}: {e}")
        
        return scraped

    def scrape_humor_sources(
        self,
        max_sources: int = 3,
        max_items_per_source: int = 5,
    ) -> List[ScrapedContent]:
        """Scrape curated humor repositories for joke material."""
        collected: List[ScrapedContent] = []

        for source in self.humor_sources[:max_sources]:
            url = source['url']
            if not self._is_allowed_url(url):
                logger.warning(f"Skipping humor source outside safelist: {url}")
                continue
            try:
                self._respect_rate_limit()
                response = self.session.get(url, timeout=self.REQUEST_TIMEOUT)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                text = self._extract_main_content(soup)
                jokes = self._extract_jokes_from_text(text, max_items_per_source)
                for idx, joke in enumerate(jokes):
                    collected.append(
                        ScrapedContent(
                            url=url,
                            title=f"{source['name']} Humor Snippet {idx + 1}",
                            content=joke['text'],
                            content_type='humor',
                            source=source['name'],
                            timestamp=datetime.now(),
                            relevance_score=0.75,
                            tags=['humor', 'joke'] + source.get('tags', []),
                            metadata={
                                'source_type': 'humor',
                                'humor_style': joke.get('style', 'general'),
                                'length': len(joke['text']),
                            },
                        )
                    )
                logger.info(
                    f"Scraped {len(jokes)} humor samples from {source['name']}"
                )
            except requests.HTTPError as http_err:
                logger.error(f"HTTP error scraping humor source {url}: {http_err}")
            except Exception as exc:
                logger.error(f"Error scraping humor source {url}: {exc}")

        if collected:
            self.scraped_content.extend(collected)
        return collected

    def _extract_jokes_from_text(self, text: str, max_items: int = 5) -> List[Dict[str, str]]:
        """Extract candidate jokes/observations from raw text."""
        if not text:
            return []

        candidates = re.split(r"\n{2,}", text)
        jokes: List[Dict[str, str]] = []

        for chunk in candidates:
            normalized = chunk.strip()
            if len(normalized) < 40:
                continue
            lower = normalized.lower()
            if not any(trigger in lower for trigger in ['joke', 'laugh', 'funny', 'setup', 'punchline', 'humor']):
                # allow concise observational lines
                if len(normalized) < 200:
                    pass
                else:
                    continue
            style = self._infer_humor_style(normalized)
            jokes.append({'text': normalized[:800], 'style': style})
            if len(jokes) >= max_items:
                break

        return jokes

    @staticmethod
    def _infer_humor_style(text: str) -> str:
        """Best-effort classification of humor style."""
        lower = text.lower()
        if any(keyword in lower for keyword in ['setup', 'punchline']):
            return 'setup-punchline'
        if any(keyword in lower for keyword in ['story', 'audience', 'stage']):
            return 'storytelling'
        if any(keyword in lower for keyword in ['data', 'computer', 'code', 'algorithm', 'debug']):
            return 'tech'
        if '?' in text and len(text) < 240:
            return 'observational'
        if len(text) < 120:
            return 'one-liner'
        return 'general'

    def scrape_urls(self, urls: Iterable[str]) -> List[ScrapedContent]:
        """Scrape arbitrary safelisted URLs (used by self-healing/learning requests)."""
        results: List[ScrapedContent] = []
        for url in urls:
            if not url:
                continue
            if not self._is_allowed_url(url):
                logger.warning(f"Skipping non-safelisted URL: {url}")
                continue
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.replace('www.', '')
                if domain in {"youtube.com", "youtu.be"}:
                    video_content = self._scrape_youtube_video(url)
                    if video_content:
                        results.append(video_content)
                    continue

                self._respect_rate_limit()
                response = self.session.get(url, timeout=self.REQUEST_TIMEOUT)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.find('title').text.strip() if soup.find('title') else url
                content = self._extract_main_content(soup)
                scraped_content = ScrapedContent(
                    url=url,
                    title=title,
                    content=content,
                    content_type='manual_scrape',
                    source=domain,
                    timestamp=datetime.now(),
                    relevance_score=0.6,
                    tags=['manual', 'custom'],
                    metadata={'source_type': 'manual'}
                )
                results.append(scraped_content)
            except (requests.HTTPError, requests.Timeout) as http_err:
                logger.error(f"HTTP error scraping {url}: {http_err}")
            except Exception as exc:
                logger.error(f"Error scraping {url}: {exc}")
        # Track scraped content for later ingestion
        if results:
            self.scraped_content.extend(results)
        return results
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from HTML"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find main content areas
        main_content = []
        
        # Common content selectors
        content_selectors = [
            'main',
            'article',
            '.content',
            '.documentation',
            '.markdown-body',
            '.prose',
            'div[class*="content"]',
            'div[class*="main"]'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    text = element.get_text(strip=True)
                    if len(text) > 100:  # Filter out very short content
                        main_content.append(text)
                break
        
        # Fallback to body content
        if not main_content:
            body_text = soup.get_text(strip=True)
            if len(body_text) > 200:
                main_content.append(body_text)
        
        # Join and clean content
        content = '\n'.join(main_content)
        content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
        content = content[:5000]  # Limit content length
        
        return content
    
    def _find_conversation_elements(self, soup: BeautifulSoup) -> List:
        """Find conversation elements in HTML"""
        conversation_elements = []
        
        # Look for common conversation patterns
        conversation_selectors = [
            '.conversation',
            '.chat',
            '.dialogue',
            '.example',
            '.demo',
            'pre',
            'code',
            'blockquote'
        ]
        
        for selector in conversation_selectors:
            elements = soup.select(selector)
            conversation_elements.extend(elements)
        
        return conversation_elements
    
    def _calculate_relevance(self, content: str, topic: str) -> float:
        """Calculate relevance score for content"""
        relevance = 0.5  # Base relevance
        
        # Check for topic keywords
        topic_keywords = topic.split('-')
        for keyword in topic_keywords:
            if keyword.lower() in content.lower():
                relevance += 0.1
        
        # Check for conversation patterns
        for pattern_type, patterns in self.learning_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    relevance += 0.05
        
        # Check content length (longer content might be more relevant)
        if len(content) > 1000:
            relevance += 0.1
        elif len(content) > 500:
            relevance += 0.05
        
        return min(1.0, relevance)
    
    def learn_from_scraped_content(self, scraped_content: List[ScrapedContent]) -> Dict[str, Any]:
        """Learn patterns from scraped content"""
        learning_results = {
            'conversation_patterns': {},
            'response_templates': {},
            'technical_knowledge': {},
            'best_practices': {},
            'total_content_processed': len(scraped_content)
        }
        
        conversation_patterns = {}
        response_templates = {}
        technical_knowledge = {}
        
        for content in scraped_content:
            # Extract conversation patterns
            patterns = self._extract_conversation_patterns(content.content)
            for pattern in patterns:
                if pattern not in conversation_patterns:
                    conversation_patterns[pattern] = []
                conversation_patterns[pattern].append({
                    'source': content.source,
                    'relevance': content.relevance_score,
                    'timestamp': content.timestamp
                })
            
            # Extract response templates
            templates = self._extract_response_templates(content.content)
            for template in templates:
                if template not in response_templates:
                    response_templates[template] = []
                response_templates[template].append({
                    'source': content.source,
                    'relevance': content.relevance_score,
                    'timestamp': content.timestamp
                })
            
            # Extract technical knowledge
            tech_knowledge = self._extract_technical_knowledge(content.content)
            for topic, info in tech_knowledge.items():
                if topic not in technical_knowledge:
                    technical_knowledge[topic] = []
                technical_knowledge[topic].append({
                    'info': info,
                    'source': content.source,
                    'relevance': content.relevance_score,
                    'timestamp': content.timestamp
                })
        
        learning_results['conversation_patterns'] = conversation_patterns
        learning_results['response_templates'] = response_templates
        learning_results['technical_knowledge'] = technical_knowledge
        
        return learning_results
    
    def _extract_conversation_patterns(self, content: str) -> List[str]:
        """Extract conversation patterns from content"""
        patterns = []
        
        for pattern_type, pattern_list in self.learning_patterns.items():
            if pattern_type == 'conversation_patterns':
                for pattern in pattern_list:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    patterns.extend(matches)
        
        return list(set(patterns))  # Remove duplicates
    
    def _extract_response_templates(self, content: str) -> List[str]:
        """Extract response templates from content"""
        templates = []
        
        # Look for common response patterns
        response_patterns = [
            r'I can help you.*?\.',
            r'Let me explain.*?\.',
            r'Based on.*?\.',
            r'I recommend.*?\.',
            r'The best approach.*?\.',
            r'You should.*?\.',
            r'Here\'s how.*?\.',
            r'To.*?\, you need.*?\.',
            r'First.*?\, then.*?\.'
        ]
        
        for pattern in response_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            templates.extend(matches)
        
        return list(set(templates))
    
    def _extract_technical_knowledge(self, content: str) -> Dict[str, str]:
        """Extract technical knowledge from content"""
        knowledge = {}
        
        for pattern_type, pattern_list in self.learning_patterns.items():
            if pattern_type == 'technical_patterns':
                for pattern in pattern_list:
                    matches = re.findall(pattern + r'.*?\.', content, re.IGNORECASE)
                    for match in matches:
                        # Extract the topic
                        topic = re.search(r'(\w+(?:\s+\w+)*)', match)
                        if topic:
                            topic_text = topic.group(1).strip()
                            knowledge[topic_text] = match.strip()
        
        return knowledge
    
    def scrape_all_sources(self, max_pages_per_source: int = 3, max_examples_per_source: int = 5) -> Dict[str, Any]:
        """Scrape all configured sources"""
        all_scraped = []
        
        # Scrape AI documentation
        for source in self.ai_model_sources:
            scraped = self.scrape_ai_documentation(source, max_pages_per_source)
            all_scraped.extend(scraped)
        
        # Scrape conversation examples
        for source in self.conversation_sources:
            scraped = self.scrape_conversation_examples(source, max_examples_per_source)
            all_scraped.extend(scraped)
        
        # Learn from scraped content
        learning_results = self.learn_from_scraped_content(all_scraped)

        # Store the combined scraped content so downstream ingestion can use it
        self.scraped_content = all_scraped.copy()
        
        return {
            'scraped_content': all_scraped,
            'learning_results': learning_results,
            'total_sources': len(self.ai_model_sources) + len(self.conversation_sources),
            'scraping_timestamp': datetime.now()
        }

    def search_youtube_videos(self, queries: List[str], max_per_query: int = 3) -> List[str]:
        """Return a list of YouTube video URLs for the provided queries."""
        discovered: List[str] = []
        seen_ids = set()
        for query in queries:
            try:
                encoded = quote_plus(query)
                search_url = f"https://www.youtube.com/results?search_query={encoded}"
                if not self._is_allowed_url(search_url):
                    logger.warning(f"Skipping search outside safelist: {search_url}")
                    continue
                self._respect_rate_limit()
                response = self.session.get(search_url, timeout=self.REQUEST_TIMEOUT)
                response.raise_for_status()
                matches = re.findall(r"watch\?v=([A-Za-z0-9_-]{11})", response.text)
                count = 0
                for video_id in matches:
                    if video_id in seen_ids:
                        continue
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    if not self._is_allowed_url(video_url):
                        continue
                    seen_ids.add(video_id)
                    discovered.append(video_url)
                    count += 1
                    if count >= max_per_query:
                        break
            except Exception as exc:
                logger.error(f"YouTube search failed for '{query}': {exc}")
        return discovered

    def _scrape_youtube_video(self, url: str) -> Optional[ScrapedContent]:
        """Fetch transcript/text plus metadata for a YouTube video URL."""
        video_id = self._extract_youtube_id(url)
        if not video_id:
            logger.warning(f"Could not determine YouTube video ID for {url}")
            return None

        transcript_text = self._get_youtube_transcript(video_id)
        soup = None
        page_text = None
        try:
            self._respect_rate_limit()
            response = self.session.get(url, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
            page_text = response.text
            soup = BeautifulSoup(response.content, 'html.parser')
        except Exception as exc:
            logger.warning(f"Unable to fetch YouTube page for metadata ({url}): {exc}")

        if not transcript_text and soup:
            transcript_text = self._extract_main_content(soup)

        if not transcript_text:
            logger.warning(f"No transcript or fallback text available for {url}")
            return None

        metadata = self._extract_youtube_metadata(video_id, url, soup, page_text)
        title = metadata.get('title') or f"YouTube Video {video_id}"
        source_name = metadata.get('author') or metadata.get('channel') or 'youtube'

        return ScrapedContent(
            url=url,
            title=title,
            content=transcript_text,
            content_type='youtube_transcript',
            source=source_name,
            timestamp=datetime.now(),
            relevance_score=0.8,
            tags=['youtube', 'video', 'custom'],
            metadata=metadata,
        )

    def _extract_youtube_id(self, url: str) -> Optional[str]:
        parsed = urlparse(url)
        if 'youtu.be' in parsed.netloc:
            return parsed.path.lstrip('/') or None
        if 'youtube.com' in parsed.netloc:
            query = parse_qs(parsed.query)
            return query.get('v', [None])[0]
        return None

    def set_transcript_pause(self, seconds: float) -> None:
        self.transcript_pause_seconds = max(0.0, float(seconds))

    def _get_youtube_transcript(self, video_id: str) -> Optional[str]:
        def _format_transcript(raw_items: List[Dict[str, Any]]) -> Optional[str]:
            if not raw_items:
                return None
            lines = [item.get('text', '').strip() for item in raw_items if item.get('text')]
            text = '\n'.join(line for line in lines if line)
            return text.strip() or None

        try:
            if self.transcript_pause_seconds:
                time.sleep(self.transcript_pause_seconds)
            api = YouTubeTranscriptApi()
            transcript_items: Optional[List[Dict[str, Any]]] = None
            if hasattr(YouTubeTranscriptApi, 'get_transcript'):
                # Legacy API signature (<=0.6)
                transcript_items = api.get_transcript(video_id)
            else:
                # Newer versions expose fetch via transcript list
                transcript_items = (
                    api
                    .list(video_id)
                    .find_transcript(['en', 'en-US', 'en-GB'])
                    .fetch()
                )
            return _format_transcript(transcript_items)
        except (TranscriptsDisabled, NoTranscriptFound):
            logger.warning(f"Transcript not available for video {video_id}")
            return None
        except Exception as exc:
            logger.error(f"Error retrieving YouTube transcript for {video_id}: {exc}")
            return None

    def _extract_youtube_metadata(
        self,
        video_id: str,
        url: str,
        soup: Optional[BeautifulSoup],
        raw_text: Optional[str],
    ) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {
            'source_type': 'youtube',
            'video_id': video_id,
            'original_url': url,
            'title': f"YouTube Video {video_id}",
        }

        if soup:
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    script_content = script.string
                    if not script_content:
                        continue
                    data = json.loads(script_content)
                    nodes = data if isinstance(data, list) else [data]
                except (json.JSONDecodeError, TypeError):
                    continue
                for node in nodes:
                    if not isinstance(node, dict):
                        continue
                    if node.get('@type') == 'VideoObject':
                        metadata['title'] = node.get('name', metadata['title'])
                        metadata['description'] = node.get('description', metadata.get('description'))
                        metadata['published_at'] = node.get('uploadDate') or node.get('datePublished') or metadata.get('published_at')
                        metadata['duration'] = node.get('duration', metadata.get('duration'))
                        author = node.get('author') or node.get('creator')
                        author_name = None
                        author_url = None
                        if isinstance(author, dict):
                            author_name = author.get('name')
                            author_url = author.get('url')
                        elif isinstance(author, list) and author:
                            first = author[0]
                            if isinstance(first, dict):
                                author_name = first.get('name')
                                author_url = first.get('url')
                        if author_name:
                            metadata['author'] = author_name
                        if author_url:
                            metadata['author_url'] = author_url
                        break
                if metadata.get('author'):
                    break

        if raw_text:
            owner_match = re.search(r'"ownerChannelName":"([^"]+)"', raw_text)
            if owner_match and not metadata.get('author'):
                metadata['author'] = owner_match.group(1)
            publish_match = re.search(r'"publishDate":"([0-9\-T:Z]+)"', raw_text)
            if publish_match and not metadata.get('published_at'):
                metadata['published_at'] = publish_match.group(1)

        # Fallback to oEmbed for title/author if still missing
        try:
            oembed = self.session.get(
                f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json",
                timeout=self.REQUEST_TIMEOUT,
            )
            if oembed.ok:
                oembed_data = oembed.json()
                metadata.setdefault('title', oembed_data.get('title'))
                metadata.setdefault('author', oembed_data.get('author_name'))
                metadata.setdefault('author_url', oembed_data.get('author_url'))
        except Exception:
            pass

        metadata.setdefault('author', 'youtube')
        metadata.setdefault('published_at', 'unknown date')
        return metadata

    def ingest_into_knowledgebase(self, knowledgebase: Any, min_relevance: float = 0.6, top_k: int = 20) -> Dict[str, Any]:
        """Push scraped content directly into the knowledgebase."""
        if not knowledgebase:
            return {'success': False, 'message': 'Knowledgebase not available'}

        added = 0
        attempted = 0
        prioritized = sorted(self.scraped_content, key=lambda c: c.relevance_score, reverse=True)[:top_k]

        for item in prioritized:
            if item.relevance_score < min_relevance:
                continue

            entries: List[str]
            if item.metadata.get('source_type') == 'youtube':
                chunks = self._chunk_text(item.content, chunk_size=900, overlap=150)
                if not chunks:
                    chunks = [item.content[:900]]
                entries = [
                    self._format_youtube_chunk(item, chunk_text, idx + 1, len(chunks))
                    for idx, chunk_text in enumerate(chunks)
                ]
            else:
                entries = [f"{item.title}: {item.content[:4000]}"]

            for entry in entries:
                attempted += 1
                embedding = self._simple_embedding(entry)
                try:
                    success = knowledgebase.add_knowledge(
                        content=entry,
                        embedding=embedding,
                        source=item.source,
                        category=item.metadata.get('source_type', 'web_scrape')
                    )
                    if success:
                        added += 1
                except Exception as exc:
                    logger.error(f"KB ingest failed for {item.url}: {exc}")

        return {
            'success': True,
            'items_attempted': attempted,
            'items_ingested': added,
        }

    def _chunk_text(self, text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
        """Split long text into overlapping chunks to preserve full transcripts."""
        if not text:
            return []
        normalized = text.strip()
        if not normalized:
            return []
        chunk_size = max(chunk_size, 300)
        overlap = max(0, min(overlap, chunk_size // 2))
        chunks = []
        start = 0
        text_len = len(normalized)
        while start < text_len:
            end = min(text_len, start + chunk_size)
            chunk = normalized[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= text_len:
                break
            start = max(0, end - overlap)
        return chunks

    def _format_youtube_chunk(
        self,
        item: ScrapedContent,
        chunk: str,
        index: int,
        total: int,
    ) -> str:
        meta = item.metadata or {}
        author = meta.get('author', item.source)
        published = meta.get('published_at', 'unknown date')
        original_url = meta.get('original_url', item.url)
        title = item.title
        header = (
            f'Transcript excerpt {index}/{total} from YouTube video "{title}" '
            f'by {author} (published {published}).\nOriginal URL: {original_url}\n\n'
        )
        return header + chunk

    def _simple_embedding(self, text: str, dimension: int = 768) -> List[float]:
        """Simple deterministic embedding placeholder (hash-based)."""
        content_hash = re.sub(r'[^a-f0-9]', '', (json.dumps(text)[:dimension * 2]).lower())
        if not content_hash:
            content_hash = '0' * dimension * 2
        embedding = [float(int(c, 16) % 100) / 100 for c in content_hash[:dimension]]
        if len(embedding) < dimension:
            embedding.extend([0.0] * (dimension - len(embedding)))
        return embedding
    
    def save_scraped_data(self, data: Dict[str, Any], filename: str = None) -> str:
        """Save scraped data to file"""
        if filename is None:
            filename = f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert datetime objects to strings for JSON serialization
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif is_dataclass(obj):
                return convert_datetime(asdict(obj))
            elif isinstance(obj, dict):
                return {k: convert_datetime(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime(item) for item in obj]
            else:
                return obj
        
        serializable_data = convert_datetime(data)
        
        filepath = f"knowledge/{filename}"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Scraped data saved to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving scraped data: {e}")
            return None

# Global instance
web_scraper = WebScraper()
