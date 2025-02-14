# Instalar dependencias y configurar filtro git
Luego de haber descargado e instalado `ILOG CPLEX Optimization Studio` de la página oficial de IBM, seguir estos pasos.

- Crear un entorno python
  `python -m venv .venv`
- Activarlo
  `source .venv/bin/activate`
- Instalar dependencias
  `pip install -r requirements.txt`
- Para poder utilizar docplex
  `./.venv/bin/python [ruta_en_la_que_se_instaló_el_sw_de_ibm]/python/setup.py install`

- Para configurar un filtro para que git no agregue cambios de metadata de los notebooks (como la execution_count de las celdas)
  `./configure_cleaning_for_git.sh`

# Ejecutar
Para ejecutar, se puede correr las celdas de los distintos notebooks.