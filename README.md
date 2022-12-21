# A Brazilian News Website Data Acquisition Library for Python
> pyBrNews Project, made with ❤️ by Lucas Rodrigues (<a href="https://github.com/NepZR/" target="_blank">@NepZR</a>).

<h4 style="text-align: justify;"> O projeto pyBrNews é uma biblioteca em desenvolvimento capaz de realizar a aquisição de dados de notícias e comentários de plataformas de notícias brasileiras, totalmente produzida na linguagem Python e utilizando como núcleo a biblioteca <a href="https://requests.readthedocs.io/projects/requests-html/en/latest/">requests-HTML</a>.


<h4>A biblioteca também está disponível para download e instalação via PIP no PyPI! Acesse <a href="https://pypi.org/project/pyBrNews">clicando aqui</a>.</h4>

 <h5>🇺🇸 You are reading the Portuguese Brazilian version of this README. To read the English version, click <a href="https://github.com/NepZR/pyBrNews/blob/main/README_ENG.md">here</a>.</h5>

<h4 style="color: red">Sobre esta branch [`college/app-project`]: dedicada exclusivamente para o projeto da disciplina de Arquitetura e Desempenho de Banco de Dados e não reflete recursos que podem subir para produção. A única exceção é o suporte ao ElasticSearch, que será trazido para a `master` depois de totalmente testado.</h4>

---

### 📲 Instalação

- **Utilizando o Gerenciador de Pacotes do Python (PIP), a partir do PyPI:**
  ```shell
  pip install pyBrNews
  ```
- **Utilizando o Gerenciador de Pacotes do Python (PIP), a partir da fonte (GitHub):**
  ```shell
  pip install git+https://github.com/NepZR/pyBrNews.git
  ```
- **Gerando o arquivo Wheel e instalando diretamente da fonte (GitHub):**
  ```shell
  git clone https://github.com/NepZR/pyBrNews.git && cd pyBrNews/
  ```
  ```shell
  python setup.py bdist_wheel
  ```
  ```shell
  pip install dist/pyBrNews-x.x.x-py3-none-any.whl --force-reinstall
  ```
  > Obs.: Substitua o x.x.x pela versão correspondente.

---

<h3 style="text-align: justify;">
  📰 Sites e tipos de captura suportados
</h3>

<table>
    <tr>
      <td><b>Nome do site</b></td>
      <td><b>Notícias</b></td>
      <td><b>Comentários</b></td>
      <td><b>URL</b></td>
    </tr>
    <tr>
      <td>Portal G1</td>
      <td>✅ Funcional</td>
      <td>🚧️ Em pausa</td>
      <td><a href="https://g1.globo.com/">Link</a></td>
    </tr>
    <tr>
      <td>Folha de São Paulo</td>
      <td>✅ Funcional</td>
      <td>✅ Funcional</td>
      <td><a href="https://www.folha.uol.com.br/">Link</a></td>
    </tr>
    <tr>
      <td>Exame</td>
      <td>✅ Funcional</td>
      <td>⚠️ Não suportado</td>
      <td><a href="https://exame.com/">Link</a></td>
    </tr>
    <tr>
      <td>Metrópoles</td>
      <td>🚧️ Em pausa</td>
      <td>🚧️ Em pausa</td>
      <td><a href="https://www.metropoles.com/">Link</a></td>
    </tr>
</table>

> **Banco de Dados**: <br>- Utilizando MongoDB (<a href="https://www.mongodb.com/docs/drivers/pymongo/">pyMongo</a>), suportado desde Outubro 28, 2022. Também com suporte a sistema de arquivos local (JSON / CSV), desde Outubro 30, 2022.<br><b style="color: limegreen">Novidade:</b><br> - Adicionado suporte para o ElasticSearch (<a href="https://opensearch.org/docs/latest/clients/python/">opensearchpy</a>) com migração de dados de duas vias (MongoDB para ElasticSearch e vice-versa), desde Dezembro 20, 2022.<br><a href="https://github.com/NepZR/pyBrNews/blob/main/config/database.py"><b>Módulos responsáveis</b></a>:<br> `pyBrNews.config.database.PyBrNewsDB`, `pyBrNews.config.database.PyBrNewsFS`, `pyBrNews.config.database.PyBrNewsES` e `pyBrNews.config.database.PyBrNewsDBMigration`.

> **Informações adicionais:**<br> - Para utilizar o sistema de armazenamento de arquivos localmente (JSON / CSV), defina o parâmetro `use_database=False` nos crawlers do pacote `news`. Exemplo: `crawler = pyBrNews.news.g1.G1News(use_database=False)`. Por padrão, está definido como `True` e utiliza a base de dados do MongoDB da classe `PyBrNewsDB`. 
---

<h3 style="text-align: justify;">
  ⌨️ Métodos disponíveis para utilização
</h3>

#### Pacote `news`
~~~python
def parse_news(self,
               news_urls: List[Union[str, dict]],
               parse_body: bool = False,
               save_html: bool = True) -> Iterable[dict]:
    """
    Extracts all the data from the article in a given news platform by iterating over a URL list. Yields a 
    dictionary containing all the parsed data from the article.

    Parameters:
        news_urls (List[str]): A list containing all the URLs or a data dict to be parsed from a given platform.
        parse_body (bool): Defines if the article body will be extracted.
        save_html (bool): Defines if the HTML bytes from the article will be extracted.
    Returns:
         Iterable[dict]: Dictionary containing all the article parsed data.
    """
~~~

~~~python
def search_news(self,
                keywords: List[str],
                max_pages: int = -1) -> List[Union[str, dict]]:
    """
    Extracts all the data or URLs from the news platform based on the keywords given. Returns a list containing the
    URLs / data found for the keywords.

    Parameters:
        keywords (List[str]): A list containing all the keywords to be searched in the news platform.
        max_pages (int): Number of pages to have the articles URLs extracted from. 
                         If not set, will catch until the last possible.
    Returns:
         List[Union[str, dict]]: List containing all the URLs / data found for the keywords.
    """
~~~

#### Pacote `config.database`

- Classe `PyBrNewsDB`
~~~python
def set_connection(self, host: str = "localhost", port: int = 27017) -> None:
    """
    Sets the connection host:port parameters for the MongoDB. By default, uses the standard localhost:27017 for
    local usage.
    
    Parameters:
         host (str): Hostname or address to connect.
         port (int): Port to be used in the connection.
    """
~~~

~~~python
def insert_data(self, parsed_data: dict) -> None:
    """
    Inserts the parsed data from a news article or extracted comment into the DB Backend (MongoDB - pyMongo).
    
    Parameters: 
        parsed_data (dict): Dictionary containing the parsed data from a news article or comment.
    Returns:
        None: Shows a success message if the insertion occurred normally. If not, shows an error message.
    """
~~~

~~~python
def check_duplicates(self, parsed_data: dict) -> bool:
    """
    Checks if the parsed data is already in the database and prevents from being duplicated 
    in the crawler execution.
    
    Parameters: 
        parsed_data (dict): Dictionary containing the parsed data from a news article or comment.
    Returns:
        bool: True if the given parsed data is already in the database. False if not.
    """
~~~

- Classe `PyBrNewsFS`
~~~python
def set_save_path(self, fs_save_path: str) -> None:
    """
    Sets the save path for all the exported data generated by this Class.

    Example: set_save_path(fs_save_path="/home/ubuntu/newsData/")

    Parameters:
         fs_save_path (str): Desired save path directory, ending with a slash.
    """
~~~

~~~python
def to_json(self, parsed_data: dict) -> None:
    """
    Using the parsed data dictionary from a news article or a comment, export the data as an individual JSON file.

    Parameters:
        parsed_data (dict): Dictionary containing the parsed data from a news article or a comment.
    """
~~~

~~~python
def export_all_data(self, full_data: List[dict]) -> None:
    """
    By a given list of dictionaries containing the parsed data from news or comments, export in a CSV file
    containing all data.

    Parameters:
        full_data (List[dict]): List containing the dictionaries of parsed data.
    """
~~~

---

<h3 style="text-align: justify;">
  👨🏻‍💻 Desenvolvedor do projeto
</h3>

<table style="display: flex; align-itens: center; justify-content: center;">
  <tr>
    <td align="center"><a href="https://github.com/NepZR"><img style="width: 150px; height: 150;" src="https://avatars.githubusercontent.com/u/37887926" width="100px;" alt=""/><br /><sub><b>Lucas Darlindo Freitas Rodrigues</b></sub></a><br /><sub><b>Data Engineer | Dev. Backend Python</sub></a><br /><a href="https://www.linkedin.com/in/lucasdfr"><sub><b>LinkedIn (lucasdfr)</b></sub></a></td>
  </tr>
<table>
