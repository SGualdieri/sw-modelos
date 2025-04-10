#!/bin/bash
# Este script configura el filtro definido en .gitattributes (escribe en el .git/config local de este repositorio)
# Configura git para excluir la metadata generada en las celdas de los notebooks de git, para no committearla-
git config --local filter.clean_ipynb.clean "jq --indent 1 '(.cells[] | select(has(\"execution_count\")) | .execution_count) = null  \
| .metadata = {\"language_info\": {\"name\": \"python\", \"pygments_lexer\": \"ipython3\"}} \
| .cells[].metadata = {}'"
git config --local filter.clean_ipynb.smudge "cat"
git config --local filter.clean_ipynb.required true