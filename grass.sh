sudo apt update -y && apt install -y python3 python3-venv pip
git clone https://github.com/zefzhou/Grass-new && cd Grass-new

# 检查 pyenv 是否安装了 Python 3.12.3
if ! pyenv versions | grep -q "3.12.3"; then
    echo "Python 3.12.3 not installed. Installing..."
    pyenv install 3.12.3
else
    echo "Python 3.12.3  already installed."
fi

screen -S grass
pyenv shell 3.12.3
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
python main.py
