sudo apt update -y & 
python3 -m venv venv &
venv/bin/pip install --upgrade pip & 
venv/bin/pip install -r requirements.txt &
sudo venv/bin/python3 asset_discovery_tool.py
