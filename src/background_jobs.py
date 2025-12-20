"""
Background jobs for Re-ID system
Run these periodically to maintain system health
"""

import requests
import time
from datetime import datetime, timedelta
import schedule

BASE_URL = "http://localhost:8000"

def close_stale_tracks():
    """
    Close tracks that haven't been seen in 5+ minutes
    Run every minute
    """
    print(f"\n[{datetime.now()}] Running: Close stale tracks")
    
    try:
        # Get all active tracks
        response = requests.get(f"{BASE_URL}/api/reid/active-tracks")
        tracks = response.json()['active_tracks']
        
        closed_count = 0
        now = datetime.now()
        
        for track in tracks:
            # Parse timestamp
            last_seen_str = track['last_seen'].replace('Z', '+00:00')
            last_seen = datetime.fromisoformat(last_seen_str)
            
            # Check if stale (not seen in 5 minutes)
            minutes_ago = (now - last_seen.replace(tzinfo=None)).total_seconds() / 60
            
            if minutes_ago > 5:
                # Close this track
                close_response = requests.post(
                    f"{BASE_URL}/api/reid/tracks/{track['global_track_id']}/close"
                )
                
                if close_response.status_code == 200:
                    closed_count += 1
                    print(f"  ✓ Closed stale track: {track['worker_name'] or 'Unknown'} "
                          f"(last seen {minutes_ago:.1f} min ago)")
        
        print(f"  Total closed: {closed_count}")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")

def update_low_confidence_tracks():
    """
    Re-run identification for tracks with low confidence
    Run every 5 minutes
    """
    print(f"\n[{datetime.now()}] Running: Update low confidence tracks")
    
    try:
        # Get active tracks
        response = requests.get(f"{BASE_URL}/api/reid/active-tracks")
        tracks = response.json()['active_tracks']
        
        updated_count = 0
        
        for track in tracks:
            # Skip if no embedding available
            if not track['feature_vector']:
                continue
            
            # Get current confidence from global_tracks
            # (You'd need to add this to the endpoint)
            # For now, assume we can check
            
            # Re-run search if confidence < 85
            search_response = requests.post(
                f"{BASE_URL}/api/reid/search-embedding",
                json={
                    "feature_vector": track['feature_vector'],
                    "threshold": 0.85,
                    "max_results": 1,
                    "search_active_only": False
                }
            )
            
            # Update logic here...
            # This is placeholder
        
        print(f"  Total updated: {updated_count}")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")

def cleanup_old_embeddings():
    """
    Remove old/low-quality embeddings to keep DB clean
    Run daily
    """
    print(f"\n[{datetime.now()}] Running: Cleanup old embeddings")
    
    # This would be a SQL query to:
    # 1. Keep only top 5 highest quality embeddings per worker
    # 2. Delete embeddings older than 90 days (except primary)
    # 3. Ensure each worker has at least 1 primary embedding
    
    print("  Cleanup logic would run here")

def generate_daily_report():
    """
    Generate daily statistics report
    Run at midnight
    """
    print(f"\n[{datetime.now()}] Running: Generate daily report")
    
    try:
        # Get stats
        stats_response = requests.get(f"{BASE_URL}/api/stats/summary")
        stats = stats_response.json()
        
        # Get alerts
        alerts_response = requests.get(f"{BASE_URL}/api/alerts?hours=24")
        alerts = alerts_response.json()
        
        print("\n" + "="*60)
        print(f" DAILY REPORT - {datetime.now().strftime('%Y-%m-%d')} ")
        print("="*60)
        
        print(f"\nHelmet Compliance:")
        compliance = stats['helmet_compliance_today']
        print(f"  Compliant: {compliance['compliant']}")
        print(f"  Violations: {compliance['violations']}")
        print(f"  Total detections: {compliance['total']}")
        print(f"  Compliance rate: {compliance['compliance_rate_percent']}%")
        
        print(f"\nAlerts (24h):")
        alert_counts = {}
        for alert in alerts:
            alert_type = alert['alert_type']
            alert_counts[alert_type] = alert_counts.get(alert_type, 0) + 1
        
        for alert_type, count in alert_counts.items():
            print(f"  {alert_type}: {count}")
        
        print("="*60)
        
    except Exception as e:
        print(f"  ✗ Error: {e}")

def schedule_jobs():
    """Set up all scheduled jobs"""
    
    # Every minute
    schedule.every(1).minutes.do(close_stale_tracks)
    
    # Every 5 minutes
    schedule.every(5).minutes.do(update_low_confidence_tracks)
    
    # Daily at 2 AM
    schedule.every().day.at("02:00").do(cleanup_old_embeddings)
    
    # Daily at midnight
    schedule.every().day.at("00:00").do(generate_daily_report)
    
    print("Background jobs scheduled:")
    print("  - Close stale tracks: Every 1 minute")
    print("  - Update low confidence: Every 5 minutes")
    print("  - Cleanup embeddings: Daily at 2 AM")
    print("  - Daily report: Daily at midnight")
    print("\nRunning... (Press Ctrl+C to stop)")

if __name__ == "__main__":
    # Check API is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
    except:
        print("✗ Error: API is not running!")
        exit(1)
    
    # Schedule all jobs
    schedule_jobs()
    
    # Run immediately once for testing
    print("\nRunning initial cleanup...")
    close_stale_tracks()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(1)