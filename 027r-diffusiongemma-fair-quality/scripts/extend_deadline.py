from pathlib import Path
from datetime import datetime
# 186 minutes after the dedicated session was created; leaves stop/download headroom under 5 CU.
deadline=datetime.fromisoformat('2026-10-14T23:51:03.689487+00:00').timestamp()+186*60
Path('/content/r027r/deadline').write_text(str(deadline));print(datetime.fromtimestamp(deadline).isoformat())
