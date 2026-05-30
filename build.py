import os
import re
import json
import requests
import markdown
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader

# Mengambil username dari environment variable GitHub Actions, default ke "voltonics" jika lokal
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "voltonics") 

def fetch_github_contributions(username):
    """
    Mengambil data kontribusi resmi menggunakan GitHub GraphQL API v4 dengan Token.
    """
    # Membaca token rahasia yang diset di GitHub Secret (Sama dengan di deploy.yml)
    token = os.getenv("PORTFOLIO_GRAPHQL_TOKEN")
    
    if not token:
        print("Peringatan: PORTFOLIO_GRAPHQL_TOKEN tidak ditemukan di environment. Menggunakan data fallback.")
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
        if response.status_code == 200:
            res_data = response.json()
            
            if "errors" in res_data:
                print(f"GraphQL Error: {res_data['errors'][0]['message']}")
                return generate_fallback_data()
                
            weeks = res_data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
            
            contributions = {}
            for week in weeks:
                for day in week["contributionDays"]:
                    contributions[day["date"]] = day["contributionCount"]
            return contributions
        else:
            print(f"Peringatan: API GitHub merespon dengan status {response.status_code}. Menggunakan data fallback.")
    except Exception as e:
        print(f"Peringatan: Gagal terhubung ke GraphQL API ({e}). Menggunakan data fallback.")
        
    return generate_fallback_data()

def generate_fallback_data():
    today = datetime.now()
    fallback = {}
    for i in range(365):
        date_str = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        fallback[date_str] = (i % 7) * 2
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
        
    num_points = len(filtered_data)
    if num_points < 2:
        return {"poly": "", "line": "", "points": [], "labels": [], "count": "0", "desc": "no data"}

    max_val = max([item[1] for item in filtered_data])
    max_val = max_val if max_val > 0 else 5
    
    points = []
    x_step = width / (num_points - 1)
    
    for idx, (dt, count) in enumerate(filtered_data):
        x = idx * x_step
        y = height - 20 - ((count / max_val) * (height - 40))
        points.append([round(x, 1), round(y, 1)])
        
    line_str = " ".join([f"{pt[0]},{pt[1]}" for pt in points])
    poly_str = f"0,{height} " + line_str + f" {width},{height}"
    
    labels = []
    if days_range == 7:
        labels = [item[0].strftime('%a') for item in filtered_data]
        desc_text = "in the last week"
    elif days_range == 30:
        indices = [0, int(num_points*0.25), int(num_points*0.5), int(num_points*0.75), num_points-1]
        labels = [filtered_data[i][0].strftime('%b %d') for i in indices]
        desc_text = "in the last month"
    else:
        indices = [0, int(num_points*0.25), int(num_points*0.5), int(num_points*0.75), num_points-1]
        labels = [filtered_data[i][0].strftime('%b') for i in indices]
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
    content_data = {'narrative_html': '', 'academic': [], 'experience': [], 'projects': []}
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
        items = projects_match.group(1).strip().split('\n- ')
        for item in items:
            if not item.strip(): continue
            title = re.search(r'title:\s*(.*)', item)
            cat = re.search(r'category:\s*(.*)', item)
            link = re.search(r'link:\s*(.*)', item)
            if title:
                content_data['projects'].append({
                    'title': title.group(1).strip(),
                    'category': cat.group(1).strip() if cat else 'Project',
                    'link': link.group(1).strip() if link else '#'
                })

    return content_data

def build_portfolio():
    if not os.path.exists('docs'):
        os.makedirs('docs')

    data = parse_content_markdown('projects.md')

    print(f"Menghubungkan ke GitHub untuk mengambil aktivitas kontribusi @{GITHUB_USERNAME}...")
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
        chart_context=chart_context
    )

    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(output_html)
    
    print("Sukses: docs/index.html telah berhasil dibuat secara dinamis!")

if __name__ == '__main__':
    build_portfolio()