prerequisites:
#install docker
	apt-get install ca-certificates curl
	install -m 0755 -d /etc/apt/keyrings
	curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
	echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
	apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
	
install:
#set up bolognese
	docker build -t bolognese-cli . -f bolognese.dockerfile
	docker build -t exdc-cli . -f doi.dockerfile

python:
#set up python
	python3 -m venv venv
	. venv/bin/activate
	python3 -m pip install -r requirements.txt
	
uv:
	curl -LsSf https://astral.sh/uv/install.sh | sh
	uv init exdc
	cd exdc
	uv add -r ../requirements.txt

run:
	. venv/bin/activate
	fastapi dev app/main.py --reload