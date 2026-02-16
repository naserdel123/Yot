import aiohttp
from config import YOUTUBE_API_KEY

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"

async def search_youtube(query: str, max_results: int = 5):
    """البحث في يوتيوب باستخدام API"""
    
    params = {
        'part': 'snippet',
        'q': query,
        'key': YOUTUBE_API_KEY,
        'maxResults': max_results,
        'type': 'video',
        'videoDuration': 'any'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(YOUTUBE_API_URL, params=params) as response:
            if response.status != 200:
                return []
            
            data = await response.json()
            
            results = []
            for item in data.get('items', []):
                video_id = item['id']['videoId']
                snippet = item['snippet']
                
                # الحصول على تفاصيل إضافية (المدة والمشاهدات)
                details = await get_video_details(session, video_id)
                
                results.append({
                    'id': video_id,
                    'title': snippet['title'],
                    'channel': snippet['channelTitle'],
                    'duration': details.get('duration', 'غير معروف'),
                    'views': details.get('views', 0),
                    'thumbnail': snippet['thumbnails']['high']['url']
                })
            
            return results

async def get_video_details(session, video_id: str):
    """الحصول على تفاصيل الفيديو"""
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        'part': 'contentDetails,statistics',
        'id': video_id,
        'key': YOUTUBE_API_KEY
    }
    
    async with session.get(url, params=params) as response:
        if response.status != 200:
            return {}
        
        data = await response.json()
        items = data.get('items', [])
        
        if not items:
            return {}
        
        item = items[0]
        content_details = item.get('contentDetails', {})
        statistics = item.get('statistics', {})
        
        # تحويل مدة ISO 8601
        duration = content_details.get('duration', 'PT0M0S')
        formatted_duration = parse_duration(duration)
        
        return {
            'duration': formatted_duration,
            'views': int(statistics.get('viewCount', 0))
        }

def parse_duration(duration: str) -> str:
    """تحويل مدة ISO 8601 إلى صيغة مقروءة"""
    import re
    
    # استخراج الساعات والدقائق والثواني
    hours = re.search(r'(\d+)H', duration)
    minutes = re.search(r'(\d+)M', duration)
    seconds = re.search(r'(\d+)S', duration)
    
    h = int(hours.group(1)) if hours else 0
    m = int(minutes.group(1)) if minutes else 0
    s = int(seconds.group(1)) if seconds else 0
    
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    else:
        return f"{m}:{s:02d}"
        