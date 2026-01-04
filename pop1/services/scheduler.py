from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pop1.parser.runner import update_parse
from pop1.config import PARSE_INTERVAL_MINUTES

def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_parse, "interval", minutes=PARSE_INTERVAL_MINUTES)
    scheduler.start()
