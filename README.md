<img src="https://img.shields.io/badge/python-3.11-blue" alt="Supported Python version"> <img src="https://img.shields.io/static/v1?logo=uv&label=uv&message=5.1.0&color=blue"> <img src="https://img.shields.io/static/v1?logo=streamlit&label=streamlit&message=1.41.0&color=blue">


# Personalized map

Web interface based on streamlit to generate a map with personalized scatter plot.

## Quickstart

### Set up

1. Install uv (v0.5.10):
   1. For macOS / Linux `curl -LsSf https://astral.sh/uv/0.5.10/install.sh | sh`
   2. For windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/0.5.10/install.ps1 | iex"`
2. Create virtual environment: `uv sync`


## Launch local web server

```sh
uv run streamlit run app.py
```
