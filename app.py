from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
import csv
import os
import time

app = FastAPI()

CSV = "history.csv"


def ai_summary(title, desc):

    text = (title + " " + desc).lower()

    if "python" in text:
        return "Educational / Developer"

    elif "shop" in text:
        return "E-commerce"

    elif "news" in text:
        return "News"

    elif "ai" in text:
        return "AI / Technology"

    return "General Website"

def calculate_score(
links,
images,
speed,
status
):

    score = 100

    if status != 200:
        score -= 40

    if speed > 3:
        score -= 20

    if links < 20:
        score -= 10

    if images < 5:
        score -= 10

    return max(
        score,
        0
    )

def analyze(url):

    try:

        start = time.time()

        headers = {
            "User-Agent":
            "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        title = (
            soup.title.text.strip()
            if soup.title
            else "No Title"
        )

        description = soup.find(
            "meta",
            attrs={
                "name":
                "description"
            }
        )

        description = (
            description.get(
                "content"
            )
            if description
            else "-"
        )

        h1 = soup.find("h1")

        h1 = (
            h1.text.strip()
            if h1
            else "-"
        )

        links = soup.find_all("a")

        domain = urlparse(
            url
        ).netloc

        internal = 0

        for l in links:

            href = l.get(
                "href"
            )

            if href and domain in href:

                internal += 1

        images = len(
            soup.find_all(
                "img"
            )
        )

        language = (
            soup.html.get(
                "lang"
            )
            if soup.html
            else "-"
        )

        speed = round(
            time.time()
            -
            start,
            2
        )

        size = round(
            len(
                response.content
            )
            /
            1024,
            2
        )

        return {

            "domain": domain,

            "title": title,

            "desc": description,

            "heading": h1,

            "status":
            response.status_code,

            "links":
            len(
                links
            ),

            "internal":
            internal,

            "images":
            images,

            "language":
            language,

            "speed":
            speed,

            "size":
            size,

           "summary":
ai_summary(
    title,
    description
),

"score":
calculate_score(

len(
    links
),

images,

speed,

response.status_code

)

        }

    except Exception:

        return {

            "domain": url,

            "title": "Failed",

            "desc": "-",

            "heading": "-",

            "status": "Error",

            "links": 0,

            "internal": 0,

            "images": 0,

            "language": "-",

            "speed": 0,

            "size": 0,

            "summary": "Unavailable"

        }


@app.get("/", response_class=HTMLResponse)
def home():

    return """

<!DOCTYPE html>

<html>

<head>

<title>

WebScope

</title>

<style>

*{

margin:0;

padding:0;

box-sizing:border-box;

}

body{

background:

linear-gradient(
135deg,
#020617,
#081228
);

color:white;

font-family:Arial;

}

nav{

display:flex;

justify-content:space-between;

padding:30px 80px;

background:

rgba(
255,
255,
255,
0.03
);

}

.logo{

font-size:34px;

font-weight:bold;

}

.menu{

display:flex;

gap:40px;

align-items:center;

}

.menu a{

color:white;

text-decoration:none;

font-size:20px;

transition:.3s;

}

.menu a:hover{

color:#60a5fa;

transform:
translateY(
-2px
);

}

.hero{

padding:120px;

text-align:center;

}

.hero h1{

font-size:88px;

}

.hero p{

font-size:28px;

margin-top:20px;

color:#94a3b8;

}

textarea{

margin-top:50px;

width:850px;

height:250px;

max-width:95%;

padding:30px;

border:none;

border-radius:25px;

font-size:20px;

}

button{

margin-top:35px;

padding:20px 60px;

font-size:24px;

background:

linear-gradient(
90deg,
#2563eb,
#7c3aed
);

border:none;

border-radius:18px;

color:white;

cursor:pointer;

}

.cards{

display:flex;

justify-content:center;

gap:25px;

flex-wrap:wrap;

padding:80px;

}

.card{

width:320px;

padding:35px;

border-radius:22px;

background:

rgba(
255,
255,
255,
0.05
);

}

.section{

padding:120px;

text-align:center;

}

.footer{

padding:40px;

text-align:center;

color:#64748b;

}

</style>

</head>

<body>

<nav>

<div class="logo">

🌐 WebScope

</div>

<div class="menu">

<a href="/">

Dashboard

</a>

<a href="#features">

Features

</a>

<a href="#about">

About

</a>

<a href="/download">

Export

</a>

</div>

</nav>

</nav>

<div class="hero">

<h1>

Website Intelligence Platform

</h1>

<p>

Analyze websites • Compare performance • Export insights

</p>

<form method="post">

<textarea

name="urls"

placeholder="

https://python.org
https://github.com
https://wikipedia.org

"

>

</textarea>

<br>

<button>

Analyze Websites

</button>

</form>

</div>

<div class="cards">

<div class="card">

<h2>

⚡ Fast

</h2>

<p>

Parallel scraping engine

</p>

</div>

<div class="card">

<h2>

📊 Analytics

</h2>

<p>

Website intelligence dashboard

</p>

</div>

<div class="card">

<h2>

📁 Export

</h2>

<p>

CSV reports

</p>

</div>

</div>

<div class="section">

<h1>

About Project

</h1>

<br>

<p>

WebScope is a modern Website Intelligence Platform that analyzes websites at scale using Python and FastAPI. The platform performs parallel website processing, extracts metadata, measures performance indicators, analyzes internal links and media assets, generates intelligent summaries, and delivers downloadable analytics reports through a responsive dashboard interface.

</p>

</div>

<div class="footer">

Built by Jivan • Python • FastAPI

</div>

</body>

</html>

"""

@app.post("/", response_class=HTMLResponse)
def scrape(
    urls: str = Form(...)
):

    urls = [

        x.strip()

        for x in urls.splitlines()

        if x.strip()

    ]

    with ThreadPoolExecutor(
        max_workers=5
    ) as ex:

        results = list(
            ex.map(
                analyze,
                urls
            )
        )

    header = not os.path.exists(
        CSV
    )

    with open(
        CSV,
        "a",
        newline=""
    ) as f:

        writer = csv.writer(
            f
        )

        if header:

            writer.writerow([

                "Domain",

                "Title",

                "Status",

                "Links",

                "Images",

                "Language",

                "Speed",

                "Summary"

            ])

        for r in results:

            writer.writerow([

                r["domain"],

                r["title"],

                r["status"],

                r["links"],

                r["images"],

                r["language"],

                r["speed"],

                r["summary"]

            ])

    html = f"""

<body style="
background:#050816;
color:white;
font-family:Arial;
">

<h1 style="
text-align:center;
padding:30px;
">

📊 Dashboard

</h1>

<div style="
display:flex;
justify-content:center;
gap:20px;
flex-wrap:wrap;
">

<div style="
background:#2563eb;
padding:20px;
border-radius:20px;
width:220px;
">

<h3>Total Sites</h3>

<h1>{len(results)}</h1>

</div>

<div style="
background:#059669;
padding:20px;
border-radius:20px;
width:220px;
">

<h3>Success</h3>

<h1>

{
sum(
1
for r in results
if r["status"] == 200
)

}

</h1>

</div>

</div>

<div style="
display:grid;
grid-template-columns:
repeat(
auto-fit,
minmax(
420px,
1fr
)
);

gap:20px;

padding:30px;
">

"""

    for r in results:

        html += f"""

<div style="
background:#111827;
padding:25px;
border-radius:20px;
">

<h2>
🌐 {r["domain"]}
</h2>

<hr>

<p>
📝 {r["title"]}
</p>

<p>
📄 {r["desc"]}
</p>

<p>
🏷 {r["heading"]}
</p>

<p>
📶 {r["status"]}
</p>

<p>
🔗 {r["links"]}
</p>

<p>
🧭 {r["internal"]}
</p>

<p>
🖼 {r["images"]}
</p>

<p>
🌍 {r["language"]}
</p>

<p>
⚡ {r["speed"]} sec
</p>

<p>
📦 {r["size"]} KB
</p>

<p>
🤖 {r["summary"]}
</p>

</div>

"""

    html += """

</div>

<div style="
text-align:center;
padding:50px;
">

<a
href="/download"
style="
background:#2563eb;
padding:18px 35px;
color:white;
border-radius:15px;
text-decoration:none;
"
>

📥 Download CSV

</a>

<br><br>

<a
href="/"
style="
color:#60a5fa;
"
>

← Back

</a>

</div>

</body>

"""

    return html


@app.get("/download")
def download():

    return FileResponse(
        CSV,
        filename="scraper_history.csv"
    )