# A Brazilian News Website Data Acquisition Library for Python
> pyBrNews Project, made with ❤️ by Lucas Rodrigues (<a href="https://github.com/NepZR/" target="_blank">@NepZR</a>).

<h4 style="text-align: justify;">
  The pyBrNews project is a Python 3 library in development for tasks of data acquisition in Brazilian News Websites, capable for extracting news and comments from this platforms and with it's core utilizing the <a href="https://requests.readthedocs.io/projects/requests-html/en/latest/">requests-HTML</a> library.
</h4>

<h4>💾 pyBrNews Library is also available for download and install on PyPI! <a href="https://pypi.org/project/pyBrNews">Click here</a>.

<h5>🇧🇷 Você está lendo a versão em Inglês deste README. Para ler a versão em Português Brasileiro, <a href="https://github.com/NepZR/pyBrNews/blob/main/README.md">clique aqui</a>.</h5>

---

### 📲 Installation

- **Using Python Package Manager (PIP), from PyPI:**
  ```shell
  pip install pyBrNews
  ```
- **Using Python Package Manager (PIP), from source (GitHub):**
  ```shell
  pip install git+https://github.com/NepZR/pyBrNews.git
  ```
- **Building wheel and installing it directly from source (GitHub):**
  ```shell
  git clone https://github.com/NepZR/pyBrNews.git && cd pyBrNews/
  ```
  ```shell
  python setup.py bdist_wheel
  ```
  ```shell
  pip install dist/pyBrNews-x.x.x-py3-none-any.whl --force-reinstall
  ```
  > Obs.: Replace x.x.x with the version.
  

---

<h3 style="text-align: justify;">
  📰 Websites and capture groups supported
</h3>

<table>
    <tr>
      <td><b>Website name</b></td>
      <td><b>News</b></td>
      <td><b>Comments</b></td>
      <td><b>URL</b></td>
    </tr>
    <tr>
      <td>Portal G1</td>
      <td>✅ Working</td>
      <td>⌨️ In progress</td>
      <td><a href="https://g1.globo.com/">Link</a></td>
    </tr>
    <tr>
      <td>Folha de São Paulo</td>
      <td>✅ Working</td>
      <td>✅ Working</td>
      <td><a href="https://www.folha.uol.com.br/">Link</a></td>
    </tr>
    <tr>
      <td>Exame</td>
      <td>✅ Working</td>
      <td>⚠️ Not supported</td>
      <td><a href="https://exame.com/">Link</a></td>
    </tr>
    <tr>
      <td>Metrópoles</td>
      <td>⌨️ In progress</td>
      <td>⌨️ In progress</td>
      <td><a href="https://www.metropoles.com/">Link</a></td>
    </tr>
</table>

> **Database**: using MongoDB (<a href="https://www.mongodb.com/docs/drivers/pymongo/">pyMongo</a>), supported since October 28th, 2022.<br><a href="https://github.com/NepZR/pyBrNews/blob/main/config/database.py"><b>Internal Module</b></a>: `pyBrNews.config.database.PyBrNewsDB`
---

<h3 style="text-align: justify;">
  ⌨️ Available methods
</h3>

#### ● Package: `news`
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

#### ● Package: `config.database`

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

---

<h3 style="text-align: justify;">
  👨🏻‍💻 Project Developer
</h3>

<table style="display: flex; align-itens: center; justify-content: center;">
  <tr>
    <td align="center"><a href="https://github.com/NepZR"><img style="width: 150px; height: 150;" src="https://avatars.githubusercontent.com/u/37887926" width="100px;" alt=""/><br /><sub><b>Lucas Darlindo Freitas Rodrigues</b></sub></a><br /><sub><b>Data Engineer | Backend Python Dev.</sub></a><br /><a href="https://www.linkedin.com/in/lucasdfr"><sub><b>LinkedIn (lucasdfr)</b></sub></a></td>
  </tr>
<table>
