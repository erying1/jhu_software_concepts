from urllib import request
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.thegradcafe.com/survey/?q=computer+science&pp=50"

req = request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = request.urlopen(req).read().decode("utf-8")

soup = BeautifulSoup(html, "html.parser")

table = soup.find("table")
rows = table.find_all("tr")
print(f"Found {len(rows)} rows")

print(rows)

data = []

for row in rows:
    cells = row.find_all("td")
    if len(cells) < 6:
        continue
    data.append([
        cells[0].get_text(strip=True),
        cells[1].get_text(strip=True),
        cells[2].get_text(strip=True),
        cells[3].get_text(strip=True),
        cells[4].get_text(strip=True),
        cells[5].get_text(strip=True),
    ])

df = pd.DataFrame(data, columns=[
    "Institute", "Program", "Decision", "Status", "Date Added", "Notes"
])

df.to_csv(
    r"C:\Users\Eric\Documents\GitHub\jhu_software_concepts\module_2\gradcafe.csv",
    index=False,
    encoding="utf-8"
)
