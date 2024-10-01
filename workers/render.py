from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from glob import glob
# Diretório do script atual
current_directory = Path(__file__).resolve().parent

# Diretório dos templates
templates_directory = current_directory / 'templates'

# Configurando o Jinja2 para carregar templates do diretório
template = Environment(loader=FileSystemLoader(str(templates_directory)))

if __name__ == '__main__':
    # Testando o template
    template_vars = {
        'title': 'Hello, World!',
        'body': 'This is a simple Jinja2 template.',
        'team': 'Team!'
    }
    template_content = template.get_template('base.html').render(template_vars)
    print(template_content)