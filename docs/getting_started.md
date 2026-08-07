# Getting Started

Welcome to the project! This guide will help you set up the static site generator locally.

## Prerequisites

Before you begin, ensure you have the following installed on your machine:
- **Python 3.10+**
- **Git**
- **pip** (Python package installer)

## Installation Steps

1. **Clone the Repository**
   Open your terminal and clone the repository using the following command:
   ```bash
   git clone https://github.com/zakyislm/zakyislm.github.io.git
   cd zakyislm.github.io
   ```

2. **Install Dependencies**
   The project uses a few Python packages such as `Jinja2` for templating and `Markdown` for content parsing. Install them via:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Environment Variables**
   Create a `.env` file in the root of the project to provide the necessary tokens. This is optional but highly recommended to fetch real contribution data from GitHub:
   ```env
   GITHUB_USERNAME=zakyislm
   PORTFOLIO_GRAPHQL_TOKEN=your_github_personal_access_token
   DATABASE_URL=your_neondb_postgres_url
   ```

4. **Build the Site**
   Run the main build script to generate the static site output:
   ```bash
   python build.py
   ```
   The generated HTML files will be placed inside the `docs/` folder.

5. **Preview Locally**
   You can serve the generated static files locally to preview the site:
   ```bash
   cd docs
   python -m http.server 8000
   ```
   Open your browser and navigate to `http://localhost:8000`.

---
[Next: Architecture and Build →](./architecture_and_build.md)
