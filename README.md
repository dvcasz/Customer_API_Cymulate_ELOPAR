# Cymulate API Data Collector - ELOPAR

Este projeto em Python é uma ferramenta para coletar e exportar dados de segurança da plataforma Cymulate para o cliente ELOPAR, consumindo diferentes dados da API através de linha de comando.

---

## Estrutura do Projeto

A arquitetura do projeto foi pensada para ser modular, permitindo a fácil adição de novos módulos e a manutenção do código.

---    

## Configuração

### 1. Pré-requisitos

Certifique-se de ter o Python 3.7+ instalado. É recomendado usar um ambiente virtual (venv).

### 2. Instalação das dependências

```bash
pip install -r requirements.txt
```

### 3. Configuração do arquivo .env

Copie o arquivo `.env` e configure sua chave da API Cymulate:

```env
# Configurações da API Cymulate para ELOPAR
CYMULATE_XTOKEN=sua_chave_api_cymulate_aqui
CLIENTE=ELOPAR
```

**⚠️ IMPORTANTE:** Substitua `sua_chave_api_cymulate_aqui` pela sua chave real da API Cymulate.

---

## Como Usar

### Execução via linha de comando

```bash
# Usando intervalo padrão de 6 meses (6 meses atrás até hoje)
python main.py

# Especificando datas customizadas
python main.py --start-date 2024-01-01 --end-date 2024-01-31

# Usando forma abreviada
python main.py -s 2024-01-01 -e 2024-01-31
```

### Parâmetros

- `--start-date` ou `-s`: Data de início da coleta (formato: YYYY-MM-DD)
  - **Padrão:** 6 meses atrás da data atual
- `--end-date` ou `-e`: Data de fim da coleta (formato: YYYY-MM-DD)
  - **Padrão:** Data atual

**📅 Intervalo Padrão:** Se nenhuma data for especificada, o script coletará dados dos últimos 6 meses automaticamente.

### Ajuda

```bash
python main.py --help
```

---

## Exemplos Práticos

### 1. Coleta com intervalo padrão (6 meses)
```bash
# Coleta dados dos últimos 6 meses automaticamente
python main.py
```

### 2. Coleta de período específico
```bash
# Dados de janeiro de 2024
python main.py -s 2024-01-01 -e 2024-01-31

# Dados do último trimestre de 2024
python main.py --start-date 2024-10-01 --end-date 2024-12-31
```

### 3. Coleta de período recente
```bash
# Últimos 30 dias (especificar datas manualmente)
python main.py -s 2024-09-28 -e 2024-10-28
```

---

## Módulos Coletados

O script coleta dados dos seguintes módulos Cymulate:

1. **immediate-threats** - Ameaças imediatas
2. **mail** - Segurança de email
3. **browsing** - Navegação web
4. **waf** - Web Application Firewall
5. **edr** - Endpoint Detection and Response
6. **dlp** - Data Loss Prevention
7. **hopper** - Lateral movement

---

## Saída

Os relatórios são salvos em:
- `./unified_reports` - Relatórios dos módulos
- `./history` - Históricos dos assessments

---

### Configurar as Chaves de API

Para manter suas chaves seguras, o projeto usa um arquivo de configuração.

- Crie a pasta config na raiz do projeto.
- Dentro dela, crie um arquivo chamado tokens.json.
- Adicione sua chave da API da Cymulate no seguinte formato:

{
    "xtoken": "SUA_CHAVE_AQUI"
}

**Importante:** Este arquivo é ignorado pelo _.gitignore_ para que suas credenciais não sejam versionadas.



## Contribuições

Sinta-se à vontade para abrir uma issue ou enviar um pull request para melhorias ou correções.
