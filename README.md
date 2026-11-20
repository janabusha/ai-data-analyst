# Intelligent Data Analysis Assistant

An interactive Streamlit application for exploring uploaded datasets and receiving AI-assisted insights grounded in Python computations.

This is a personal learning and portfolio project focused on Python, pandas, data analysis, visualization, testing, Streamlit, and local/cloud AI integration.

## Features

- Upload and inspect datasets
- Dataset overview and column summaries
- Missing-value and duplicate detection
- Numeric and categorical distributions
- Correlation analysis
- Tool-grounded dataset questions
- Local Ollama support for development
- Ollama Cloud support for deployment

## Project structure

```text
ai-data-analyst/
├── app.py
├── analysis.py
├── chart_visuals.py
├── model_client.py
├── requirements.txt
├── styles.css
├── assets/
├── test/
├── ui/
└── views/
```

## Local setup

### 1. Clone the repository

```bash
git clone https://github.com/janabusha/ai-data-analyst.git
cd ai-data-analyst
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and start Ollama

Download Ollama from:

https://ollama.com/download

Download the local model:

```bash
ollama pull qwen3.5:4b
```

Make sure Ollama is running before starting the application.

### 5. Configure local development

Create this file:

```text
.streamlit/secrets.toml
```

Add:

```toml
MODEL_PROVIDER = "local"
```

`MODEL_NAME` is optional. The default local model is:

```text
qwen3.5:4b
```

The local configuration connects to:

```text
http://localhost:11434
```

Local inference runs on your computer and does not use the Ollama Cloud API.

### 6. Run the application

```bash
streamlit run app.py
```

## Testing with Ollama Cloud locally

To test the cloud model before deployment, change the local `.streamlit/secrets.toml` file:

```toml
MODEL_PROVIDER = "cloud"
OLLAMA_API_KEY = "your-private-api-key"
```

The default cloud model is:

```text
gpt-oss:120b
```

This configuration sends requests to Ollama Cloud and may use your cloud allowance or incur API usage according to your Ollama account.

To return to local inference, change the configuration back to:

```toml
MODEL_PROVIDER = "local"
```

## Security

Never commit API keys or local secrets.

The `.gitignore` file must contain:

```gitignore
.streamlit/secrets.toml
.env
.venv/
__pycache__/
.pytest_cache/
```

Verify that the secrets file is ignored:

```bash
git check-ignore -v .streamlit/secrets.toml
```

Never paste API keys into:

- Python files
- GitHub
- README files
- Screenshots
- Issues or pull requests

If a key is accidentally exposed, revoke it and generate a replacement immediately.

## Tests

Run the test suite with:

```bash
python -m pytest -v
```

## Technology

- Python
- pandas
- Streamlit
- Altair
- pytest
- Ollama
- Ollama Cloud API

## Status

This project is under active development as a learning and portfolio project.