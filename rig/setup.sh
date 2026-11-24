set -e
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get install -yq --no-install-recommends python3-venv python3-dev build-essential ca-certificates curl unzip zstd
python3 -m venv /root/v
/root/v/bin/pip install -q --upgrade pip
/root/v/bin/pip install -q pandas
cd /root/exp
# SQLite 3.54.1 amalgamation, checked against the sha3-256 sqlite.org lists
curl -fsSL -o sqlite.zip https://www.sqlite.org/2026/sqlite-amalgamation-3540100.zip
echo "92281c86e2957f9b9305890f9ac04204caa7b677cc868dc326d942689df28e30  sqlite.zip" > sqlite.sha3
python3 -c "import hashlib,sys; h=hashlib.sha3_256(open('sqlite.zip','rb').read()).hexdigest(); sys.exit(0 if h=='92281c86e2957f9b9305890f9ac04204caa7b677cc868dc326d942689df28e30' else 1)"
unzip -oq sqlite.zip && mv sqlite-amalgamation-3540100/sqlite3.c .
g++ -O2 -std=c++17 gen_ops.cpp -o gen_ops && ./gen_ops 1000000 > ops.bin
/root/v/bin/python make_data.py
{ python3 --version; /root/v/bin/python -c "import pandas, numpy; print('pandas', pandas.__version__, 'numpy', numpy.__version__)"; gcc --version | head -1; zstd --version; } > versions.txt
