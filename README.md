# ✈ ATC Radar

Visualizador de tráfego aéreo em tempo real construído com Python e Streamlit, consumindo dados reais da [OpenSky Network](https://opensky-network.org).

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📸 Funcionalidades

- 🗺 **Mapa interativo** com aeronaves em tempo real
- 🎨 **Coloração por altitude** — azul (cruzeiro), verde (médio), laranja (aproximação), vermelho (baixo)
- 📋 **Faixas de voo** com callsign, altitude, velocidade e país de origem
- 🔍 **Busca** por callsign
- 🚨 **Detecção de squawks de emergência** (7700, 7600, 7500)
- ⚙ **Filtros configuráveis** — altitude mínima/máxima, área de cobertura, aeronaves no solo
- 🔄 **Atualização manual** com cache de 15 segundos

---

## 🚀 Como rodar

### Pré-requisitos

- Python 3.10+
- pip

### Instalação

```bash
# Clone o repositório
git clone https://github.com/YuriMel0/atc-radar.git
cd atc-radar

# Crie e ative o ambiente virtual
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# Mac/Linux
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### Execução

```bash
streamlit run app.py
```

Acesse `http://localhost:8501` no navegador.

---

## 📦 Dependências

| Biblioteca | Uso |
|---|---|
| `streamlit` | Interface web |
| `folium` | Mapa interativo |
| `streamlit-folium` | Integração Folium + Streamlit |
| `requests` | Consumo da API OpenSky |
| `pandas` | Manipulação dos dados |

---

## 🛰 Fonte de dados

Os dados são fornecidos pela **OpenSky Network** — uma rede colaborativa e gratuita de receptores ADS-B ao redor do mundo.

- **Sem autenticação:** 100 requisições/dia, intervalo mínimo de 10s
- **Com conta gratuita:** 4.000 requisições/dia, intervalo mínimo de 5s

Cadastro gratuito em: [opensky-network.org](https://opensky-network.org/index.php?option=com_users&view=registration)

> Os dados são de uso **não comercial**, conforme os termos da OpenSky Network.

---

## 🗺 Área de cobertura padrão

Por padrão, o radar cobre o **sudeste do Brasil** (região de SBGR/SBSP):

| Parâmetro | Valor |
|---|---|
| Latitude mínima | -24.5° |
| Latitude máxima | -18.5° |
| Longitude mínima | -48.5° |
| Longitude máxima | -42.5° |

A área pode ser alterada diretamente pela sidebar do app.

---

## 🚨 Squawks monitorados

| Código | Significado |
|---|---|
| 7700 | Emergência geral |
| 7600 | Falha de rádio |
| 7500 | Sequestro |

---

## 📁 Estrutura do projeto

```
atc-radar/
├── app.py            # Aplicação principal
├── requirements.txt  # Dependências
├── .gitignore
└── README.md
```

---

## 🔮 Próximos passos

- [ ] Autenticação com OpenSky para maior rate limit
- [ ] Auto-refresh configurável
- [ ] Histórico de posições (trails)
- [ ] Filtro por país de origem
- [ ] Deploy no Streamlit Cloud

---

## 📄 Licença

MIT License — use à vontade para estudos e portfólio.
