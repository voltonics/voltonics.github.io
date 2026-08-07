# Project Documentation Index

Welcome to the internal documentation for the static site generator. This folder contains all the technical details on how the project functions, how to configure it, and how it deploys.

> [!NOTE]
> These markdown files are intended for developers working on the `legend` branch. They explain the underlying python build architecture and are strictly distinct from the generated static HTML site.

## Table of Contents

1. [Getting Started](./getting_started.md)
   *Prerequisites, cloning the repository, and local preview.*
2. [Architecture and Build System](./architecture_and_build.md)
   *How the `build.py` script functions and generates HTML.*
3. [Data and Content Management](./data_and_content.md)
   *How to update the `projects.md` file to reflect new content.*
4. [GitHub API Integration](./github_api_integration.md)
   *Fetching contribution graphs and fallback systems.*
5. [Deployment and CI/CD](./deployment_and_ci.md)
   *GitHub Actions, gh-pages branch, and NeonDB logging.*

---
[Next: Getting Started →](./getting_started.md)
