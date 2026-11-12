"""Re-submit the GPT-5.6 T fills deliberately, staggered (max 2 concurrent, 60 s apart): first attempts failed gpt3's local
sentinel verification when six 5.6 calls started together. Earlier failed attempts are kept in runs/tfill_failed/."""
import thr, step0_tfill as s
thr.MIN_GAP = 60.0
thr.parallel = lambda: 2
thr.run([k for k in s.keys if "gpt56w" in k[1]])
