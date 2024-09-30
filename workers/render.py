from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Diretório do script atual
current_directory = Path(__file__).resolve().parent

# Diretório dos templates
templates_directory = current_directory / 'templates'

# Configurando o Jinja2 para carregar templates do diretório
template = Environment(loader=FileSystemLoader(str(templates_directory)))