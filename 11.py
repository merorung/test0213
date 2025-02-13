from youtube_transcript_api import YouTubeTranscriptApi
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re

app = FastAPI()

class YouTubeURL(BaseModel):
    url: str

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats"""
    patterns = [
        r'v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'embed/([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_youtube_transcript(video_id):
    """Get transcript and format as continuous text"""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
    except:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
    
    full_text = ' '.join(entry['text'] for entry in transcript)
    full_text = re.sub(r'\s+', ' ', full_text)
    
    return full_text.strip()

@app.post("/get-transcript")
async def get_transcript(youtube_url: YouTubeURL):
    try:
        video_id = extract_video_id(youtube_url.url)
        if not video_id:
            raise HTTPException(status_code=400, detail="올바르지 않은 YouTube URL입니다.")
        
        transcript = get_youtube_transcript(video_id)
        return {"transcript": transcript}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
