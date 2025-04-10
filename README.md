# Instalar dependencias y configurar filtro git
Luego de haber descargado e instalado `ILOG CPLEX Optimization Studio` de la página oficial de IBM, seguir estos pasos.

- Crear un entorno python:

  `python -m venv .venv`

- Activarlo:

  `source .venv/bin/activate`

- Instalar dependencias:

  `pip install -r requirements.txt`


- Identificar la, llamémosla "carpeta_base", en la que se instaló ibm cplex.

  Para verificar, la carpeta es la que contiene a:

   ```
    concert  cpoptimizer  license  python       swidtag
    cplex    doc          opl      README.html  Uninstall
   ```

  Copiarse la ruta a la carpeta base, incluyendo a la carpeta_base. Llamémosla "ruta_base".

  (ej ruta_base: /home/al/otras_posibles_carpetas/[carpeta_base])

- Para poder utilizar ibm cplex:

  `./.venv/bin/python [ruta_base]/python/setup.py install`

- Para configurar un filtro para que git no agregue cambios de metadata de los notebooks (como la execution_count de las celdas) ni las imágenes generadas:

  `./configure_cleaning_for_git.sh` (recomendado)

  - Si en cambio se desea no conservar la metadata pero sí conservar las imágenes (ej plots) en los commits

    `./configure_cleaning_for_git_allow_images.sh`

  - Se recomienda no conservar las imágenes. De lo contrario cada vez que se vuelva a ejecutar un notebook, por más que no se haya hecho ningún cambio y el gráfico que se genere sea exactamente el mismo con exactamente los mismos datos, git lo interpreta como uno nuevo y committea sus bytes cada vez, quedando menos claros los diffs y poblando el history de cambios que en realidad no son cambios.

# Ejecutar
Para ejecutar, se puede correr las celdas de los distintos notebooks.

Actualmente se cuenta con datos de prueba, modificables, en `data_and_model_construction/`.

(Luego de modificar un archivo ".py", para ver los cambios reflejados desde un notebook se debe "Reiniciar kernel").
La primera vez que se intente ejecutar, si es desde un ide, preguntará qué kernel se desea usar, elegir de la lista el correspondiente a ".venv".
