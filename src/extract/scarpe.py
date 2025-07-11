import json
from httpx import Client
from parsel import Selector
from loguru import logger as log

from ..constant import DATA_DIR



# scrape travel forum list by keyword

def scrap_travel_forum_list_by_keyword(keyword: str, page: int = 1):
    client = Client(http2=True, timeout=10.0)
    log.info(f"Scraping travel forum list by keyword: {keyword}, page: {page}")
    response = client.get(f"https://search.ricksteves.com/?button=&filter=Travel+Forum&page={page}&query={keyword.replace(' ', '+')}")
    return response.text

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

def get_travel_forum_list_by_keyword(keyword: str, start_page: int = 1, end_page: int = 276):
    """Complete function to scrape and parse travel forum data"""
    posts = []
    for page in range(start_page, end_page + 1):
        html = scrap_travel_forum_list_by_keyword(keyword, page)
        posts.extend(parse_travel_forum_list_by_keyword(html))


    with open(DATA_DIR / f"posts_{keyword.replace(' ', '_')}.json", "w") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)



def scrape_post_detail(post_link: str) -> str:
    """Scrape the HTML content of a post detail page"""
    client = Client(http2=True, timeout=10.0)
    log.info(f"Scraping post detail: {post_link}")
    response = client.get(post_link)
    return response.text


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


def get_post_detail(post_link: str) -> dict:
    """Complete function to scrape and parse post detail data"""
    html = scrape_post_detail(post_link)
    return parse_post_detail(html)






if __name__ == "__main__":
    with open(DATA_DIR / "posts_audio_guide.json", "r") as f:
        posts = json.load(f)


    posts_detail = []
    for post in posts:
        posts_detail.append(get_post_detail(post["link"]))

    with open(DATA_DIR / "posts_audio_guide_detail.json", "w") as f:
        json.dump(posts_detail, f, indent=2, ensure_ascii=False)






