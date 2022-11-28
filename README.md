
# Kio estas gedcomx ?
Ĝi estas biblioteko por manipuli la gedcomx-formaton uzatan en genealogio.

Kun gedcomx, vi povas legi kaj skribi json-datumojn.  
Xml-datumoj ne estas bone subtenataj, vi ne uzu ĝin.

Por pliaj informoj pri gedcomx-formaton, vidu:
* <https://github.com/FamilySearch/gedcomx/blob/master/specifications/conceptual-model-specification.md>
* <https://github.com/FamilySearch/gedcomx/blob/master/specifications/json-format-specification.md>
* <https://www.familysearch.org/developers/docs/api/gx_json>
* <https://www.familysearch.org/developers/docs/api/fs_json>

# Instalado

1. Instalu **Python 3.7** aŭ pli novan
  
    Ekzemplo por debian :
    ```sh
    sudo apt update
    sudo apt --no-install-recommends install python3
    ```

2. Instalu `pip`
  
    Ekzemplo por debian :
    ```sh
    sudo apt update
    sudo apt --no-install-recommends install python3-pip
    ```

    Alia ekzemplo por debian :
    ```sh
    curl -sSfO 'https://bootstrap.pypa.io/get-pip.py'
    sudo python3 get-pip.py
    rm get-pip.py
    ```

3. Instalu gedcomx
    ```sh
    python3 -m pip install gedcomx-v1
    ```

# Promocio

```sh
python3 -m pip install --upgrade --force-reinstall gedcomx-v1
```

# Ekzemploj

Vidu en la dosierujo «testoj».
