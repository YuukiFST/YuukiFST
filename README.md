<div align="center">
  <a href="https://github.com/YuukiFST">
    <img src="https://raw.githubusercontent.com/YuukiFST/YuukiFST/main/header.svg" alt="yuuki — agent runtime" width="900">
  </a>
</div>

```console
❯ cat ~/.config/yuuki/profile.toml
```

```toml
[human]
name    = "Yuuki"
role    = "Fullstack Developer"
focus   = ["AI/ML", "LLMs", "agents", "CLI tooling"]
theme   = "vanta-black"          # #000000, nothing lighter

[environment]
os      = "Linux"
ui      = "terminal"             # everything else is a fallback
runtime = "herdr"                # https://herdr.dev — agents survive when I disconnect
editors = ["neovim", "coding agents"]

[stack]
python  = ["LangGraph", "FastAPI", "XGBoost", "SHAP", "Chroma", "Ollama"]
web     = ["TypeScript", "JavaScript"]
systems = ["Go", "Rust", "C++"]
```

```console
❯ yuuki agents ls --detail
```

| agent | status | what it does |
|---|---|---|
| [Omoikane](https://github.com/YuukiFST/Omoikane) | `working` | LLM-maintained personal wiki that ingests sources on its own |
| [Credit-Guard](https://github.com/YuukiFST/Credit-Guard) | `working` | XGBoost credit risk + SHAP, translated into plain text by an LLM |
| [neobank-support-chatbot](https://github.com/YuukiFST/neobank-support-chatbot) | `idle` | LangGraph supervisor, specialist agents, RAG over Chroma |
| [StackRadar](https://github.com/YuukiFST/StackRadar) | `idle` | job-market tech rankings + local RAG assistant (Ollama) |
| [agent-dotfiles](https://github.com/YuukiFST/agent-dotfiles) | `working` | skills, agents and workflows for AI coding tools |

```console
❯ yuuki whoami
```

> I build things where a model does part of the thinking and a terminal does the rest.
> Dark mode is not a preference. It is a requirement.

<sub>header rendered by <a href="bin/render">bin/render</a>, refreshed daily</sub>
