from apscheduler.schedulers.blocking import BlockingScheduler

from voc_agent.pipeline import run_weekly_ingestion


def job() -> None:
    run_id = run_weekly_ingestion(use_seed_csv=False)
    print(f"weekly job finished: {run_id}")


if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(job, "cron", day_of_week="sun", hour=2, minute=0)
    print("Scheduler started. Weekly run set for Sunday 02:00 UTC")
    scheduler.start()
