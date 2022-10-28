# A Brazilian News Website Data Acquisition Library for Python
> pyBrNews Project, made with :heart: by Lucas Rodrigues (<a href="https://github.com/NepZR/" target="_blank">@NepZR</a>).

<h4 style="text-align: justify;"> O projeto pyBrNews é uma biblioteca em desenvolvimento capaz de realizar a aquisição de dados de notícias e comentários de plataformas de notícias brasileiras, totalmente produzida na linguagem Python e utilizando como núcleo a biblioteca <a href="https://requests.readthedocs.io/projects/requests-html/en/latest/">requests-HTML</a>. Será funcional tanto em scripts, quanto em projetos feitos em ambiente interativo, como em Python Notebooks.</h4>


 <h5>🇺🇸 You are reading the Portuguese Brazilian version of this README. To read the English version, click <a href="https://github.com/NepZR/pyBrNews/blob/main/README_ENG.md">here</a>.</h5>

<h4>A biblioteca também está disponível para download e instalação via PIP no PyPI! Acesse <a href="https://pypi.org/project/pyBrNews">clicando aqui</a>.</h4>

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
      <td>⌨️ Em desenvolvimento</td>
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
      <td>⌨️ Em desenvolvimento</td>
      <td>⌨️ Em desenvolvimento</td>
      <td><a href="https://www.metropoles.com/">Link</a></td>
    </tr>
</table>

> **Banco de Dados**: utilizando MongoDB (<a href="https://www.mongodb.com/docs/drivers/pymongo/">pyMongo</a>), suportado desde Outubro 28, 2022.<br><a href="https://github.com/NepZR/pyBrNews/blob/main/config/database.py"><b>Módulo responsável</b></a>: `pyBrNews.config.database.PyBrNewsDB`
---

<h3 style="text-align: justify;">
  ⌨️ Métodos disponíveis para utilização
</h3>

> Em breve.
  
---

<h3 style="text-align: justify;">
  👨🏻‍💻 Desenvolvedor do projeto
</h3>

<table style="display: flex; align-itens: center; justify-content: center;">
  <tr>
    <td align="center"><a href="https://github.com/NepZR"><img style="width: 150px; height: 150;" src="https://avatars.githubusercontent.com/u/37887926" width="100px;" alt=""/><br /><sub><b>Lucas Darlindo Freitas Rodrigues</b></sub></a><br /><sub><b>Data Engineer | Dev. Backend Python</sub></a><br /><a href="https://www.linkedin.com/in/lucasdfr"><sub><b>LinkedIn (lucasdfr)</b></sub></a></td>
  </tr>
<table>
