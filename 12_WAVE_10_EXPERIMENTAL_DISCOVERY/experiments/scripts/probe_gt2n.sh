#!/usr/bin/env bash
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
"$D" run --rm --network none --entrypoint /bin/bash openroad/orfs:latest -c '
cd /OpenROAD-flow-scripts/flow/platforms/gt2n; ls; echo; head -60 README.md 2>/dev/null; echo; head -40 config.mk
echo ==== openroad; ls /OpenROAD-flow-scripts/tools/install/OpenROAD/bin 2>/dev/null; /OpenROAD-flow-scripts/tools/install/OpenROAD/bin/openroad -version 2>/dev/null
cd /OpenROAD-flow-scripts && git log -1 --format="ORFS %H %cd" 2>/dev/null; git -C tools/OpenROAD log -1 --format="OpenROAD %H %cd" 2>/dev/null; ls tools/OpenROAD/src 2>/dev/null | tr "\n" " "
'
