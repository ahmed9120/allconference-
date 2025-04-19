from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

app = Flask(__name__)

@app.route('/scrape-conferences', methods=['GET'])
def scrape_conferences():
    category = request.args.get('category', default='engineering-and-technology')
    place = request.args.get('place', default='alexandria')

    if not category or not place:
        return jsonify({"error": "Both category and place parameters are required"}), 400

    valid_categories = [
        "business-and-economics",
        "medical-and-health-science",
        "mathematics-and-statistics",
        "engineering-and-technology",
        "physical-and-life-sciences",
        "social-sciences-and-humanities",
        "education",
        "law"
    ]

    if category not in valid_categories:
        return jsonify({"error": "Invalid category"}), 400

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            url = f"https://allconferencealert.com/{category}/{place}.html"
            page.goto(url)
            page.wait_for_timeout(3000)  # wait for JS to load
            content = page.content()
            browser.close()

        soup = BeautifulSoup(content, 'lxml')
        table = soup.find('table', class_='table')

        if not table:
            return jsonify({"error": "No conferences found for the specified criteria"}), 404

        rows = table.find_all("tr", class_="data1")
        data = []

        for row in rows:
            date = row.find("td").get_text(strip=True)
            title_td = row.find("td", style="text-align: left")
            title = title_td.get_text(strip=True)
            link = title_td.find("a")["href"]
            venue = row.find("td").find_next("td").find_next("td").get_text(strip=True)

            data.append({
                "date": date,
                "title": title,
                "venue": venue,
                "link": link,
                "category": category.replace("-", " ").title(),
                "location": place.title()
            })

        if request.args.get('save_csv', default=False, type=bool):
            df = pd.DataFrame(data)
            filename = f"{category}_{place}_conferences.csv"
            df.to_csv(filename, index=False)
            return jsonify({
                "message": f"Scraped {len(data)} conferences",
                "data": data,
                "csv_file": filename
            })

        return jsonify({
            "count": len(data),
            "conferences": data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
