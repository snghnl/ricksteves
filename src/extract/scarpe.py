import json
import asyncio
import random
import time
from httpx import AsyncClient, HTTPStatusError
from parsel import Selector
from loguru import logger as log

from ..constant import DATA_DIR


# Constants for rate limiting
REQUEST_DELAY_MIN = 1.0  # Minimum delay between requests (seconds)
REQUEST_DELAY_MAX = 3.0  # Maximum delay between requests (seconds)
MAX_RETRIES = 3  # Maximum number of retries for failed requests
RETRY_DELAY_BASE = 2.0  # Base delay for exponential backoff


async def delay_request():
    """Add a random delay between requests to avoid rate limiting"""
    delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
    await asyncio.sleep(delay)


# scrape travel forum list by keyword

async def scrap_travel_forum_list_by_keyword(keyword: str, page: int = 1, retry_count: int = 0):
    """Scrape travel forum list with retry logic and rate limiting"""
    try:
        # Add delay before making request
        await delay_request()
        
        async with AsyncClient(http2=True, timeout=30.0) as client:
            log.info(f"Scraping travel forum list by keyword: {keyword}, page: {page}")
            response = await client.get(f"https://search.ricksteves.com/?button=&filter=Travel+Forum&page={page}&query={keyword.replace(' ', '+')}")
            
            response.raise_for_status()
            return response.text
            
    except HTTPStatusError as e:
        if e.response.status_code == 429 and retry_count < MAX_RETRIES:
            # Exponential backoff for rate limiting
            retry_delay = RETRY_DELAY_BASE ** (retry_count + 1)
            log.warning(f"Rate limited (429) on page {page}. Retrying in {retry_delay} seconds... (attempt {retry_count + 1}/{MAX_RETRIES})")
            await asyncio.sleep(retry_delay)
            return await scrap_travel_forum_list_by_keyword(keyword, page, retry_count + 1)
        else:
            log.error(f"HTTP error {e.response.status_code} on page {page}: {e}")
            raise
    except Exception as e:
        log.error(f"Unexpected error on page {page}: {e}")
        raise


def parse_travel_forum_list_by_keyword(html: str):
    selector = Selector(html)
    
    # Find all a tags with class "search-result topic"
    topic_links = selector.css('a.search-result.topic')
    
    scraped_data = []
    
    for link_element in topic_links:
        # Extract the href (link)
        link = link_element.css('::attr(href)').get()
        
        # Extract the title from the h2 element
        title = link_element.css('h2::text').get()
        
        # Extract metadata from the p element with class "metadata"
        metadata = link_element.css('p.metadata::text').get()
        
        # Clean up the data (remove extra whitespace)
        if title:
            title = title.strip()
        if metadata:
            metadata = metadata.strip()
            _ ,time, forum = metadata.split('|')
            time = time.strip()
            forum = forum.strip().replace("Posted in ", "")
            

        scraped_data.append({
            'link': link,
            'title': title,
            'time': time,
            'forum': forum
        })
    
    return scraped_data

async def get_travel_forum_list_by_keyword(keyword: str, start_page: int = 1, end_page: int = 276, max_concurrent: int = 5):
    """Complete function to scrape and parse travel forum data with concurrent processing and rate limiting"""
    posts = []
    
    # Reduce max_concurrent to avoid overwhelming the server
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def scrape_page(page):
        async with semaphore:
            try:
                html = await scrap_travel_forum_list_by_keyword(keyword, page)
                return parse_travel_forum_list_by_keyword(html)
            except Exception as e:
                log.error(f"Failed to scrape page {page}: {e}")
                return []  # Return empty list for failed pages
    
    # Create tasks for all pages
    tasks = [scrape_page(page) for page in range(start_page, end_page + 1)]
    
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Combine all results, handling exceptions
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            log.error(f"Task {i + start_page} failed: {result}")
            continue
        posts.extend(result)

    log.info(f"Successfully scraped {len(posts)} posts")
    with open(DATA_DIR / f"posts_{keyword.replace(' ', '_')}.json", "w") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)


async def scrape_post_detail(post_link: str, retry_count: int = 0) -> str:
    """Scrape the HTML content of a post detail page with retry logic"""
    try:
        # Add delay before making request
        await delay_request()
        
        async with AsyncClient(http2=True, timeout=30.0) as client:
            log.info(f"Scraping post detail: {post_link}")
            response = await client.get(post_link)
            response.raise_for_status()
            return response.text
            
    except HTTPStatusError as e:
        if e.response.status_code == 429 and retry_count < MAX_RETRIES:
            # Exponential backoff for rate limiting
            retry_delay = RETRY_DELAY_BASE ** (retry_count + 1)
            log.warning(f"Rate limited (429) for {post_link}. Retrying in {retry_delay} seconds... (attempt {retry_count + 1}/{MAX_RETRIES})")
            await asyncio.sleep(retry_delay)
            return await scrape_post_detail(post_link, retry_count + 1)
        else:
            log.error(f"HTTP error {e.response.status_code} for {post_link}: {e}")
            raise
    except Exception as e:
        log.error(f"Unexpected error for {post_link}: {e}")
        raise


def parse_post_detail(html: str) -> dict:
    """Parse the HTML content and extract post details"""
    selector = Selector(html)
    
    # Extract URL (current page URL)
    url = selector.css('meta[property="og:url"]::attr(content)').get()
    if not url:
        # Fallback: try to get from canonical link
        url = selector.css('link[rel="canonical"]::attr(href)').get()
    
    # Extract title
    title = selector.css('h1.title::text').get()
    if title:
        title = title.strip()
    
    # Extract content (main post content)
    content_element = selector.css('article.topic .content.markdown').get()
    if content_element:
        # Get text content without HTML tags
        content = Selector(content_element).xpath('string()').get()
        content = content.strip() if content else ""
    else:
        content = ""
    
    # Extract replies
    replies = []
    reply_elements = selector.css('section#replies article.reply')
    
    for reply in reply_elements:
        reply_data = {}
        
        # Extract reply author
        author = reply.css('.author a::text').get()
        if author:
            reply_data['author'] = author.strip()
        
        # Extract reply time
        time_element = reply.css('time::attr(datetime)').get()
        if time_element:
            reply_data['time'] = time_element
        
        # Extract reply content
        reply_content_element = reply.css('.content.markdown').get()
        if reply_content_element:
            reply_content = Selector(reply_content_element).xpath('string()').get()
            reply_data['content'] = reply_content.strip() if reply_content else ""
        else:
            reply_data['content'] = ""
        
        # Extract user location if available
        location = reply.css('.user-location::text').get()
        if location:
            reply_data['location'] = location.strip()
        
        # Extract post count if available
        post_count = reply.css('.post-count::text').get()
        if post_count:
            reply_data['post_count'] = post_count.strip()
        
        replies.append(reply_data)
    
    return {
        'url': url,
        'title': title,
        'content': content,
        'replies': replies
    }


async def get_post_detail(post_link: str) -> dict:
    """Complete function to scrape and parse post detail data"""
    html = await scrape_post_detail(post_link)
    return parse_post_detail(html)


async def process_all_post_details(posts: list, max_concurrent: int = 5) -> list:
    """Process all post details concurrently with rate limiting"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_single_post(post):
        async with semaphore:
            try:
                return await get_post_detail(post["link"])
            except Exception as e:
                log.error(f"Failed to process post {post.get('link', 'unknown')}: {e}")
                return None  # Return None for failed posts
    
    # Create tasks for all posts
    tasks = [process_single_post(post) for post in posts]
    
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out None results and exceptions
    valid_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            log.error(f"Task {i} failed: {result}")
            continue
        if result is not None:
            valid_results.append(result)
    
    log.info(f"Successfully processed {len(valid_results)} out of {len(posts)} posts")
    return valid_results


async def main():
    with open(DATA_DIR / "posts_audio_guide.json", "r") as f:
        posts = json.load(f)

    posts_detail = await process_all_post_details(posts)

    with open(DATA_DIR / "posts_audio_guide_detail.json", "w") as f:
        json.dump(posts_detail, f, indent=2, ensure_ascii=False)




if __name__ == "__main__":

    # Run the async main function
    asyncio.run(main())






