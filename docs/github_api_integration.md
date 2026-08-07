# GitHub API Integration

To make the portfolio truly dynamic, the site fetches your real-time GitHub contribution history and renders it as an SVG chart.

## GraphQL Fetching
The `build.py` script sends a GraphQL query to `https://api.github.com/graphql`. It queries the `contributionsCollection` to get a 365-day calendar of commit activity for the configured `GITHUB_USERNAME`.

> [!IMPORTANT]
> The GitHub GraphQL API requires authentication. You must provide a valid Personal Access Token (PAT) via the `PORTFOLIO_GRAPHQL_TOKEN` environment variable. 

## Fallback Data Generation
If the build script cannot reach the GitHub API (e.g., rate limits, missing token, or network issues), it will **not** fail the build. Instead, it gracefully falls back to generating simulated data.

The `generate_fallback_data()` function uses a mathematical model (combining `math.sin` and `math.cos` waves with periodic spikes) to create realistic-looking pseudo-random contribution activity. This ensures the UI always renders a beautiful chart even when the API is down.

## Chart Generation
The fetched (or simulated) data is passed into the `generate_chart_data()` function. This function:
1. Filters the data based on the requested time range (7 days, 30 days, or 365 days).
2. Calculates X and Y coordinates for each data point to fit within the SVG dimensions.
3. Generates smooth Bezier curves (`C` commands) to connect the points, resulting in a fluid, continuous line chart rather than a jagged one.
4. Returns the generated SVG paths (`poly` and `line`) directly to the Jinja2 context for injection.

---
[← Previous: Data and Content](./data_and_content.md) | [Next: Deployment and CI/CD →](./deployment_and_ci.md)
