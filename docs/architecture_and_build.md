# Architecture and Build System

This project is a custom **Static Site Generator (SSG)** built with Python. It parses markdown content, fetches external data via API, and uses Jinja2 templates to compile static HTML pages.

## How it Works

The core of the architecture lies in the `build.py` script. When executed, it follows a specific sequence of operations:

1. **Initialization**
   - The script creates the `docs/` output directory if it doesn't already exist.
   
2. **Content Parsing**
   - It calls `parse_content_markdown('projects.md')` to extract structured profile data, academic history, projects, and the tech stack. This data is extracted using Regex patterns.
   
3. **Data Fetching**
   - The script connects to the GitHub GraphQL API to fetch the user's contribution data (the "GitHub graph").
   - If the API fails or no token is provided, a mathematically simulated fallback graph is generated via `generate_fallback_data()`.
   
4. **Data Processing**
   - The raw contribution data is processed by `generate_chart_data()` to generate SVG path instructions (Bezier curves and polygons) for the 7-day, 30-day, and 365-day contribution charts.
   
5. **Template Rendering**
   - The script loads the `template.html` and `404_template.html` Jinja2 templates.
   - It injects the parsed markdown data, the SVG chart contexts, and social links into the templates, and writes the output as `docs/index.html` and `docs/404.html`.
   
6. **Asset Management**
   - Favicons and other static assets are copied from `src/assets/` directly to `docs/src/assets/`.
   - SEO files such as `sitemap.xml`, `robots.txt`, and a Google Site Verification file are generated on the fly.

> [!TIP]
> **Why custom SSG?** 
> By writing a custom Python build script rather than using Jekyll or Hugo, this project has fine-grained control over how the GitHub graph SVG is generated directly into the HTML without relying on client-side JavaScript.

---
[← Previous: Getting Started](./getting_started.md) | [Next: Data and Content →](./data_and_content.md)
