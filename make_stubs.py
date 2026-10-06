# 옛 주소 스텁 생성기. app-redirect 저장소 폴더에서 python3 make_stubs.py
import os, re, json, html, urllib.request, urllib.parse
NEW = "https://macultist.kr"            # 실제 도메인으로 바꾼다
OLD = "https://app.macultist.com"
EXTRA = [  # 사이트맵에 없는 옛 경로
    "/archive/20260910.html", "/archive/20260911.html",
    "/petfee/chungbuk/720.html", "/petfee/jeonnam/720.html",
    "/petfee/chungnam/taean-gu.html", "/petfee/gyeongnam/hapcheon-gu.html",
    "/curvetrace/", "/curvetrace/about.html", "/curvetrace/privacy.html",
    "/curvetrace/guide/", "/curvetrace/guide/extraction.html",
    "/curvetrace/guide/format.html", "/curvetrace/guide/verification.html",
]
STUB = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<script>location.replace({js}+location.search+location.hash)</script>
<meta http-equiv="refresh" content="0; url={u}">
<link rel="canonical" href="{u}">
<title>주소가 바뀌었습니다</title></head>
<body><p>새 주소로 옮겼습니다: <a href="{u}">{u}</a></p></body></html>
"""
LOC = re.compile(r"<loc>\s*(.*?)\s*</loc>")

def get(url):
    return urllib.request.urlopen(url, timeout=30).read().decode("utf-8")

def save(path, text):  # URL 경로 -> 파일. 한글 경로는 풀어서 저장
    f = urllib.parse.unquote(path).lstrip("/")
    if f == "" or f.endswith("/"):
        f += "index.html"
    os.makedirs(os.path.dirname(f) or ".", exist_ok=True)
    with open(f, "w", encoding="utf-8") as fp:
        fp.write(text)

index = get(OLD + "/sitemap.xml")
save("/sitemap.xml", index)  # 옛 사이트맵도 남겨 구글이 옛 URL을 다시 읽게 한다
pages = set(EXTRA)
for sm in map(html.unescape, LOC.findall(index)):
    xml = get(sm)
    save(urllib.parse.urlsplit(sm).path, xml)
    pages |= {urllib.parse.urlsplit(html.unescape(u)).path for u in LOC.findall(xml)}
pages.discard("/")  # 루트 index.html 은 인증 메타를 넣어 따로 만든다
for p in sorted(pages):
    new = NEW + p
    save(p, STUB.format(u=html.escape(new), js=json.dumps(new)))
print(len(pages), "개 스텁 생성")
