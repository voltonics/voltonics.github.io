import os
import sys
import subprocess
from datetime import datetime, timezone, timedelta
import psycopg2

def get_git_info():
    author = "Unknown"
    commit_message = "Unknown"
    commit_sha = "Unknown"
    branch = "Unknown"
    
    # 1. Author and Commit Message
    try:
        author = subprocess.check_output(["git", "log", "-1", "--format=%an"], text=True).strip()
        commit_message = subprocess.check_output(["git", "log", "-1", "--format=%B"], text=True).strip()
        commit_sha = subprocess.check_output(["git", "log", "-1", "--format=%H"], text=True).strip()
    except Exception as e:
        print(f"Warning: Could not get git log details: {e}")
        
    # 2. Branch Name
    branch = os.getenv("GITHUB_REF_NAME")
    if not branch:
        try:
            branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
        except Exception as e:
            print(f"Warning: Could not get git branch name: {e}")
            
    # Fallback SHA
    if commit_sha == "Unknown":
        commit_sha = os.getenv("GITHUB_SHA", "Unknown")
        
    return author, commit_message, commit_sha, branch

def log_to_db():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL environment variable is not set.")
        sys.exit(1)
    status = sys.argv[1] if len(sys.argv) > 1 else "success"
    
    event_name = os.getenv("GITHUB_EVENT_NAME", "local_run")
    actor = os.getenv("GITHUB_ACTOR", "local_user")
    
    # Git info
    author, commit_message, commit_sha, branch = get_git_info()
    
    # Date & time in GMT+7 (Asia/Jakarta)
    jakarta_tz = timezone(timedelta(hours=7))
    now = datetime.now(jakarta_tz)
    updated_at = now.strftime("%A, %d/%m/%y")
    timestamp = now.strftime("%H:%M:%S")
    
    print(f"Logging: Event={event_name}, Branch={branch}, Commit={commit_sha[:7]}, Message={commit_message.splitlines()[0] if commit_message else ''}, Author={author}, Actor={actor}, Status={status}, Date={updated_at}, Time={timestamp}")
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Create table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS deploy_logs (
                id SERIAL PRIMARY KEY,
                event_name VARCHAR(100),
                branch VARCHAR(100),
                commit_sha VARCHAR(100),
                commit_message TEXT,
                author VARCHAR(255),
                actor VARCHAR(100),
                status VARCHAR(50),
                updated_at VARCHAR(100),
                timestamp VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Insert log
        cur.execute("""
            INSERT INTO deploy_logs (event_name, branch, commit_sha, commit_message, author, actor, status, updated_at, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (event_name, branch, commit_sha, commit_message, author, actor, status, updated_at, timestamp))
        
        conn.commit()
        cur.close()
        conn.close()
        print("Logged successfully to NeonDB.")
    except Exception as e:
        print(f"Error logging to NeonDB: {e}")
        sys.exit(1)

if __name__ == "__main__":
    log_to_db()
