import random
import time
from pop1.config import REQUEST_DELAY_RANGE

def sleep_random():
    time.sleep(random.uniform(*REQUEST_DELAY_RANGE))
