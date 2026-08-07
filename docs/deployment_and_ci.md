# Deployment and CI/CD

The project leverages GitHub Actions for continuous integration and continuous deployment (CI/CD) to GitHub Pages.

## Deployment Workflow

The workflow is defined in `.github/workflows/deploy.yml` and triggers automatically on:
- Pushes to the `legend` branch
- Pull requests targeting the `legend` branch
- A scheduled cron job (running every Monday at 2:00 AM UTC) to ensure the GitHub contribution graph remains up to date even if no new code is pushed.
- Manual execution via `workflow_dispatch`.

### Pipeline Steps:
1. **Checkout & Setup**: Clones the repository and sets up Python 3.10.
2. **Install Dependencies**: Installs the required packages via `pip install -r requirements.txt`.
3. **Pre-build Logging**: Triggers `db_log.py started` to record the start of a deployment in NeonDB.
4. **Clean & Build**: 
   - Deletes any old `docs/` directory.
   - Recreates an empty `docs/` folder.
   - Runs `python build.py` to generate the new static files inside `docs/`. Environment variables (like `PORTFOLIO_GRAPHQL_TOKEN`) are securely injected from GitHub Secrets during this step.
5. **Deploy**: Uses the `JamesIves/github-pages-deploy-action` to forcefully push the contents of the `docs/` folder to the `gh-pages` branch. This triggers GitHub Pages to serve the updated site.
6. **Post-build Logging**: Triggers `db_log.py success` (or `failure` if something crashed) to record the final state of the deployment.

## Database Logging (`db_log.py`)

To keep track of deployments, the system records metadata to a PostgreSQL database hosted on NeonDB. 

The script uses `subprocess` to extract the current Git author, commit message, SHA, and branch. It then connects to NeonDB using `psycopg2` and inserts a log entry into the `deploy_logs` table (creating the table automatically if it doesn't exist). 

> [!WARNING]
> Ensure the `DATABASE_URL` secret is properly configured in your repository settings, otherwise the database logging steps will fail and halt the pipeline.

---
[← Previous: GitHub API Integration](./github_api_integration.md)
