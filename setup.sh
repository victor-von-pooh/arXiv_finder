python3 -m venv venv
source ./venv/bin/activate

pip3 install -U pip
sleep 2
pip3 install -r requirements.txt

echo "export PYTHONPATH=.." >> ~/.zshrc
source ~/.zshrc