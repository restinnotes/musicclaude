"""Resume corrected pipeline after the original judge owner exits; never resend it."""
import time,json
from pathlib import Path
import run_pipeline
from completed_reports import completed_files
from prepare_reviews import ROLES
HERE=Path(__file__).resolve().parent
run_pipeline.status('waiting_for_original_judge_owner_then_corrected_validation',no_duplicate_requests=True)
while (HERE/'coordinator.lock').exists():
    time.sleep(5)
for job in ROLES:completed_files(job)
run_pipeline.main()
