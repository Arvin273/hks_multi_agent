# 1.创建一个python虚拟环境
```commandline
uv venv --seed .venv --python 3.12
```

# 2.安装依赖
```commandline
uv pip install -e .
uv pip install -e .[langchain]
uv pip install tavily-python
uv pip install -e external/aiqtoolkit-server
uv pip install langchain
uv pip install langchain_chroma
uv pip install langchain_dashscope
```

# 3.运行后端
```commandline
aiq serve --config_file configs\hackathon_config.yml --host 0.0.0.0 --port 8001
aiq serve --config_file external\aiqtoolkit-server\src\my_multi_agent\configs\multi_agent_config.yml --host 0.0.0.0 --port 8001
API文档:  http://localhost:8001/docs
```

# 4.运行前端
```commandline
cd external\aiqtoolkit-opensource-ui
npm install
npm run dev
前端界面: http://localhost:3000
```

# 5.部署到docker
```commandline
docker build -t aiq-multi-agent:latest -f Dockerfile .
docker run -d --name aiq-multi-agent -p 8001:8001 aiq-multi-agent:latest
```