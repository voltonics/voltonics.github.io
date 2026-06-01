import os
import re
import json
import requests
import markdown
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "zakyislm") 
def fetch_github_contributions(username):
    token = os.getenv("PORTFOLIO_GRAPHQL_TOKEN")
    if token:
        print(f"Actions Log: token found {token[:4]}***")
    else:
        print("Actions Log: token not found. Using fallback data...")
    if not token:
        return generate_fallback_data()
    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"bearer {token}"}
    query = """
    query($username: String!) {
      user(login: $username) {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """
    try:
        response = requests.post(url, json={"query": query, "variables": {"username": username}}, headers=headers, timeout=10)
        print(f"Actions Log: GraphQL API responded with Status Code {response.status_code}")
        
        if response.status_code == 200:
            res_data = response.json()
            if "errors" in res_data:
                print(f"Actions Log: GraphQL Error detail: {json.dumps(res_data['errors'])}")
                return generate_fallback_data() 
            weeks = res_data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
            contributions = {}
            for week in weeks:
                for day in week["contributionDays"]:
                    contributions[day["date"]] = day["contributionCount"]
            return contributions
        else:
            print(f"Actions Log: API GitHub error {response.status_code}. Detail: {response.text}")
    except Exception as e:
        print(f"Actions Log: Couldn't connect to GraphQL API ({e}). Using fallback data.")
    return generate_fallback_data()
def generate_fallback_data():
    import math
    today = datetime.now()
    fallback = {}
    current_trend = 5.0
    for i in range(365):
        date_str = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        raw_noise = math.sin(i * 0.95) * 4.5 + math.cos(i * 2.3) * 3.0
        spike = 0
        if (i * 13) % 19 == 0:
            spike = 5.0
        elif (i * 7) % 23 == 0:
            spike = -4.0
        simulated_move = current_trend + raw_noise + spike
        contribution_count = max(0, min(15, int(simulated_move)))
        fallback[date_str] = contribution_count
        current_trend += math.sin(i / 12) * 0.4
        if current_trend > 8.0: current_trend = 7.0
        if current_trend < 2.0: current_trend = 3.0
    return fallback
def generate_chart_data(contributions, days_range, width=1000, height=200):
    today = datetime.now()
    dates_list = [(today - timedelta(days=i)) for i in range(days_range)]
    dates_list.reverse()
    filtered_data = []
    total_contributions = 0
    for dt in dates_list:
        date_str = dt.strftime('%Y-%m-%d')
        count = contributions.get(date_str, 0)
        total_contributions += count
        filtered_data.append((dt, count))
    chart_points_data = []
    if days_range == 365:
        weekly_count = 0
        for idx, (dt, count) in enumerate(filtered_data):
            weekly_count += count
            if (idx + 1) % 7 == 0 or idx == len(filtered_data) - 1:
                chart_points_data.append((dt, weekly_count))
                weekly_count = 0  
    elif days_range == 30:
        two_days_count = 0
        for idx, (dt, count) in enumerate(filtered_data):
            two_days_count += count
            if (idx + 1) % 2 == 0 or idx == len(filtered_data) - 1:
                chart_points_data.append((dt, two_days_count))
                two_days_count = 0      
    else:
        chart_points_data = filtered_data
    num_points = len(chart_points_data)
    if num_points < 2:
        return {"poly": "", "line": "", "points": [], "labels": [], "count": "0", "desc": "no data"}
    max_val = max([item[1] for item in chart_points_data])
    max_val = max_val if max_val > 0 else 5
    points = []
    x_step = width / (num_points - 1)
    for idx, (dt, count) in enumerate(chart_points_data):
        x = idx * x_step
        y = height - 20 - ((count / max_val) * (height - 40))
        points.append([round(x, 1), round(y, 1)])
    line_str = " ".join([f"{pt[0]},{pt[1]}" for pt in points])
    poly_str = f"0,{height} " + line_str + f" {width},{height}"
    labels = []
    if days_range == 7:
        labels = [item[0].strftime('%a') for item in chart_points_data]
        desc_text = "in the last week"
    elif days_range == 30:
        indices = [0, int(num_points*0.25), int(num_points*0.5), int(num_points*0.75), num_points-1]
        labels = [chart_points_data[i][0].strftime('%b %d') for i in indices]
        desc_text = "in the last month"
    else:
        indices = [0, int(num_points*0.25), int(num_points*0.5), int(num_points*0.75), num_points-1]
        labels = [chart_points_data[i][0].strftime('%b') for i in indices]
        desc_text = "in the last year"
    return {
        "count": f"{total_contributions} contributions",
        "desc": desc_text,
        "poly": poly_str,
        "line": line_str,
        "points": points,
        "labels": labels
    }
def parse_content_markdown(filepath):
    content_data = {'narrative_html': '', 'academic': [], 'experience': [], 'projects': [], 'social': {}}
    if not os.path.exists(filepath):
        return content_data
    with open(filepath, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    narrative_match = re.search(r'# Personal Narrative\s*\n(.*?)(?=\n#|$)', raw_text, re.DOTALL)
    if narrative_match:
        content_data['narrative_html'] = markdown.markdown(narrative_match.group(1).strip())
    academic_match = re.search(r'# Academic Journey\s*\n(.*?)(?=\n#|$)', raw_text, re.DOTALL)
    if academic_match:
        items = academic_match.group(1).strip().split('\n- ')
        for item in items:
            if not item.strip(): continue
            inst = re.search(r'institution:\s*(.*)', item)
            prd = re.search(r'period:\s*(.*)', item)
            desc = re.search(r'description:\s*(.*)', item)
            if inst:
                content_data['academic'].append({
                    'institution': inst.group(1).strip(),
                    'period': prd.group(1).strip() if prd else '',
                    'description': desc.group(1).strip() if desc else ''
                })
    exp_match = re.search(r'# Experience\s*\n(.*?)(?=\n#|$)', raw_text, re.DOTALL)
    if exp_match:
        items = exp_match.group(1).strip().split('\n- ')
        for item in items:
            if not item.strip(): continue
            role = re.search(r'role:\s*(.*)', item)
            comp = re.search(r'company:\s*(.*)', item)
            prd = re.search(r'period:\s*(.*)', item)
            desc = re.search(r'description:\s*(.*)', item)
            if role:
                content_data['experience'].append({
                    'role': role.group(1).strip(),
                    'company': comp.group(1).strip() if comp else '',
                    'period': prd.group(1).strip() if prd else '',
                    'description': desc.group(1).strip() if desc else ''
                })
    projects_match = re.search(r'# Selected Projects\s*\n(.*?)(?=\n#|$)', raw_text, re.DOTALL)
    if projects_match:
        items = re.split(r'\n\s*-\s+', projects_match.group(1).strip())
        for item in items:
            if not item.strip(): continue
            title = re.search(r'title:\s*(.*)', item)
            cat = re.search(r'category:\s*(.*)', item)
            link = re.search(r'link:\s*["\']?(.*?)["\']?$', item, re.M)
            if title:
                content_data['projects'].append({
                    'title': title.group(1).strip(),
                    'category': cat.group(1).strip() if cat else 'Project',
                    'link': link.group(1).strip() if link else '#'
                })
    social_match = re.search(r'# Social Links\s*\n(.*?)(?=\n#|$)', raw_text, re.DOTALL)
    if social_match:
        items = social_match.group(1).strip().split('\n- ')
        for item in items:
            if not item.strip(): continue
            platform = re.search(r'platform:\s*(.*)', item)
            link = re.search(r'link:\s*(.*)', item)
            if platform and link:
                content_data['social'][platform.group(1).strip().lower()] = link.group(1).strip()
    return content_data
def generate_sitemap(base_url="https://zakyislm.github.io"):
    # Sesuaikan base_url dengan alamat live website kamu
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{base_url}/</loc>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""
    with open('docs/sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
    print("Actions Log: Successfully generated sitemap.xml")
def build_portfolio():
    if not os.path.exists('docs'):
        os.makedirs('docs')
    data = parse_content_markdown('projects.md')
    print(f"Connecting to GitHub for fetching contributions @{GITHUB_USERNAME}...")
    raw_github_data = fetch_github_contributions(GITHUB_USERNAME)
    
    chart_context = {
        'week': generate_chart_data(raw_github_data, days_range=7),
        'month': generate_chart_data(raw_github_data, days_range=30),
        'year': generate_chart_data(raw_github_data, days_range=365)
    }
    env = Environment(loader=FileSystemLoader('.'))
    env.filters['tojson'] = lambda data: json.dumps(data)
    template = env.get_template('template.html')
    output_html = template.render(
        narrative_html=data['narrative_html'],
        academic_list=data['academic'],
        experience_list=data['experience'],
        projects=data['projects'],
        social=data['social'],
        chart_context=chart_context
    )
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(output_html)
    src_favicon = 'src/assets/icons'
    dist_favicon = 'docs/src/assets/icons'
    if os.path.exists(src_favicon):
        if os.path.exists(dist_favicon):
            import shutil
            shutil.rmtree(dist_favicon)
        import shutil
        shutil.copytree(src_favicon, dist_favicon)
        print("Actions Log: Copied favicon assets to docs/src/assets/icons successfully.")
    else:
        print("Actions Log: Couldn't find src/assets/icons.")
    # with open('docs/CNAME', 'w', encoding='utf-8') as f:
    #     f.write('zakyislm.eu.org')
    # cname creations disabled until the domains are properly set up to avoid build failures due to domain issues.
    print("Actions Log: Successfully built portfolio at docs/index.html")
    generate_sitemap()
if __name__ == '__main__':
    build_portfolio()