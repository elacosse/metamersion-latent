import os
import shutil

dp_base = "/mnt/ls1_data/test_sessions"
dn_backup = "Z_BACKUPS"


subdirs = os.listdir(dp_base)
subdirs.sort()
dp_backup = os.path.join(dp_base, dn_backup)
os.makedirs(dp_backup, exist_ok=True)

for s in subdirs:
    if s==dn_backup:
        continue
    dp_out = os.path.join(dp_base, s)
    list_files_local = os.listdir(dp_out)
    if len(list_files_local) == 0:
        print(f"moving: {dp_out}")
        shutil.move(dp_out, os.path.join(dp_base, dn_backup))
