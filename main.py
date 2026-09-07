from fastapi import FastAPI, Response, Request
from fastapi.responses import StreamingResponse
import requests
from urllib.parse import urljoin, quote, unquote

app = FastAPI()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://stream.tvpure.net/"
}

@app.get("/live.m3u8")
def proxy_live(url: str, request: Request):
    target_url = unquote(url)
    try:
        res = requests.get(target_url, headers=HEADERS, timeout=10)
        
        # إذا كان الطلب ملف m3u8
        if "mpegurl" in res.headers.get("Content-Type", "").lower() or target_url.endswith(".m3u8"):
            content = res.text
            base_proxy_url = str(request.base_url) + "live.m3u8?url="
            
            lines = content.splitlines()
            new_lines = []
            
            for line in lines:
                line_str = line.strip()
                if line_str and not line_str.startswith("#"):
                    absolute_segment_url = urljoin(target_url, line_str)
                    proxied_url = base_proxy_url + quote(absolute_segment_url, safe='')
                    new_lines.append(proxied_url)
                else:
                    new_lines.append(line)
                    
            return Response(content="\n".join(new_lines), media_type="application/vnd.apple.mpegurl")
        
        # إذا كان الطلب قطعة فيديو (.ts)
        else:
            def iterfile():
                with requests.get(target_url, headers=HEADERS, stream=True, timeout=15) as r:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            yield chunk
                            
            return StreamingResponse(iterfile(), media_type=res.headers.get("Content-Type", "video/MP2T"))

    except Exception as e:
        return Response(content=f"Error: {str(e)}", status_code=500)
