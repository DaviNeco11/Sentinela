"""
Testes unitários das configurações centrais do projeto Sentinela.

Objetivo deste arquivo:
- Validar a estrutura básica do objeto de configuração
- Garantir que os caminhos principais do projeto sejam montados corretamente
- Verificar se os valores padrão existem e têm tipos esperados

Observação acadêmica:
Este teste ajuda a garantir que a camada de configuração,
base para várias outras partes do sistema, esteja funcionando corretamente.

Como este projeto utiliza uma arquitetura em camadas,
erros em configurações centrais podem comprometer rotas, serviços e testes.
"""

from pathlib import Path

from backend.core.config import Settings, settings


def test_settings_instance_exists():
    """
    Verifica se a instância global 'settings' foi criada corretamente.

    Resultado esperado:
    - settings deve ser uma instância da classe Settings
    """
    assert isinstance(settings, Settings)


def test_app_basic_settings_are_strings():
    """
    Verifica se as configurações básicas da aplicação existem
    e possuem o tipo esperado.

    Campos testados:
    - APP_NAME
    - APP_VERSION
    - APP_ENV
    """
    assert isinstance(settings.APP_NAME, str)
    assert isinstance(settings.APP_VERSION, str)
    assert isinstance(settings.APP_ENV, str)

    assert settings.APP_NAME != ""
    assert settings.APP_VERSION != ""
    assert settings.APP_ENV != ""


def test_gaia_settings_have_expected_types():
    """
    Verifica se as configurações relacionadas ao Gaia
    possuem tipos adequados.

    Campos testados:
    - GAIA_API_URL deve ser string
    - GAIA_MODEL_NAME deve ser string
    - GAIA_TIMEOUT_SECONDS deve ser inteiro
    """
    assert isinstance(settings.GAIA_API_URL, str)
    assert isinstance(settings.GAIA_MODEL_NAME, str)
    assert isinstance(settings.GAIA_TIMEOUT_SECONDS, int)

    assert settings.GAIA_API_URL != ""
    assert settings.GAIA_MODEL_NAME != ""
    assert settings.GAIA_TIMEOUT_SECONDS > 0


def test_project_paths_are_path_objects():
    """
    Verifica se os caminhos principais do projeto
    são representados por objetos Path.

    Isso é importante porque o restante do backend
    depende desses caminhos para localizar arquivos.
    """
    assert isinstance(settings.BASE_DIR, Path)
    assert isinstance(settings.BACKEND_DIR, Path)
    assert isinstance(settings.FRONTEND_DIR, Path)
    assert isinstance(settings.INDEX_FILE, Path)
    assert isinstance(settings.CSS_FILE, Path)
    assert isinstance(settings.JS_FILE, Path)


def test_backend_dir_is_inside_base_dir():
    """
    Verifica se BACKEND_DIR está contido dentro de BASE_DIR.

    Esse teste garante coerência estrutural do projeto.
    """
    assert settings.BACKEND_DIR.parent == settings.BASE_DIR


def test_frontend_dir_is_inside_base_dir():
    """
    Verifica se FRONTEND_DIR está contido dentro de BASE_DIR.
    """
    assert settings.FRONTEND_DIR.parent == settings.BASE_DIR


def test_frontend_file_names_are_correct():
    """
    Verifica se os nomes esperados dos arquivos do frontend
    foram montados corretamente.

    Isso ajuda a detectar erros de nomenclatura
    ou construção incorreta dos caminhos.
    """
    assert settings.INDEX_FILE.name == "index.html"
    assert settings.CSS_FILE.name == "styles.css"
    assert settings.JS_FILE.name == "app.js"


def test_as_dict_returns_expected_keys():
    """
    Verifica se o método as_dict() retorna um dicionário
    contendo as chaves principais esperadas.

    Esse método é útil para depuração e inspeção.
    """
    config_dict = settings.as_dict()

    expected_keys = {
        "APP_NAME",
        "APP_VERSION",
        "APP_ENV",
        "BASE_DIR",
        "BACKEND_DIR",
        "FRONTEND_DIR",
        "INDEX_FILE",
        "CSS_FILE",
        "JS_FILE",
        "GAIA_API_URL",
        "GAIA_MODEL_NAME",
        "GAIA_TIMEOUT_SECONDS",
    }

    assert isinstance(config_dict, dict)
    assert expected_keys.issubset(config_dict.keys())


def test_as_dict_returns_serializable_values():
    """
    Verifica se os valores retornados por as_dict()
    estão em formato simples e serializável.

    Como Path é convertido para string no as_dict(),
    esperamos strings e inteiros.
    """
    config_dict = settings.as_dict()

    assert isinstance(config_dict["APP_NAME"], str)
    assert isinstance(config_dict["APP_VERSION"], str)
    assert isinstance(config_dict["APP_ENV"], str)
    assert isinstance(config_dict["BASE_DIR"], str)
    assert isinstance(config_dict["BACKEND_DIR"], str)
    assert isinstance(config_dict["FRONTEND_DIR"], str)
    assert isinstance(config_dict["INDEX_FILE"], str)
    assert isinstance(config_dict["CSS_FILE"], str)
    assert isinstance(config_dict["JS_FILE"], str)
    assert isinstance(config_dict["GAIA_API_URL"], str)
    assert isinstance(config_dict["GAIA_MODEL_NAME"], str)
    assert isinstance(config_dict["GAIA_TIMEOUT_SECONDS"], int)