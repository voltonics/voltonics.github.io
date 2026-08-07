# Data and Content Management

All the content for the generated portfolio is stored in a single markdown file: `projects.md`. The `build.py` script parses this file using regular expressions to extract structured data for the Jinja2 templates.

## Structure of `projects.md`

The file is organized into distinct sections using Markdown headers (`#`). Each section has a specific format that the parser expects. 

### 1. SEO Metadata
Defines the `<meta>` tags and OpenGraph properties for the HTML `<head>`.
```markdown
# SEO Metadata
author: Zaky
title: Zaky's Portfolio
description: A showcase of my projects.
```

### 2. Profile
Defines your main introduction.
```markdown
# Profile
name: Zaky
role: Developer
slogan: Building cool things.
```

### 3. Tech Stack
List your technical skills here. Special support is included for `devicon`: if a list item starts with `devicon-`, the script will automatically map it to the corresponding colored and plain SVGs from the Devicon CDN.
```markdown
# Tech Stack
- devicon-python-plain
- devicon-react-original
```

### 4. Experience & Academic Journey
These sections use bullet points containing key-value pairs separated by colons to outline history.
```markdown
# Experience
- role: Software Engineer
  company: Tech Corp
  period: 2021 - Present
```

### 5. Selected Projects
List your portfolio projects. Links and sources can be provided in quotes.
```markdown
# Selected Projects
- title: My Awesome Project
  category: Open Source
  link: "https://example.com"
  description: A brief description.
```

## How to Update Content
To update the website's content, simply edit the values inside `projects.md` and rerun the `build.py` script. The build engine will automatically parse the new values and inject them into `docs/index.html`.

---
[← Previous: Architecture and Build](./architecture_and_build.md) | [Next: GitHub API Integration →](./github_api_integration.md)
