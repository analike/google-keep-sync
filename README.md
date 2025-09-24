# google-keep-sync

A simple unofficial client to migrate Google Keep notes from `SOURCE` account to `DEST` account.

**THIS PROJECT IS NEITHER SUPPORTED NOR ENDORSED Google.**

## Usage

- Follow this [authentication guide](https://gkeepapi.readthedocs.io/en/latest/#authenticating) to obtain `master` tokens
for both `source` and `dest` accounts.

- Create a `./.env` file and fill the authentication details.
    ```sh
    SOURCE_EMAIL='username1@gmail.com'
    SOURCE_MASTER_TOKEN='aas_et/AKpp...'
    DEST_EMAIL='username2@gmail.com'
    DEST_MASTER_TOKEN='aas_et/AKpp...'
    ````
- Create python virtual environment in `./.venv` and requirements
    ```sh
    pip -m venv ./.venv && source ./.venv/bin/activate
    pip install -r requirements.txt
    ```

- Run the program
    ```sh
    ./keep.py
    ```
