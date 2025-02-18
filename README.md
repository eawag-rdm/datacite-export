# DataCite Export

Downloads DataCite DOI records via the DataCite REST API version 2. Conceptually the process consists of 3 steps:

1. Construct a DOI list based on a user specified DOI prefix
2. Get the XML record for each DOI in the DOI list
3. Compress all the XML records into a ZIP file

## Command Line Usage

```
python app/doi_agency/datacite.py -h
```
usage: datacite.py [-h] [-d DOI] [-c CACHE] [-l LOG] [-v] [--info] [--debug] [--verbosity {0,1,2}] doi_prefix mailto

### Positional Arguments
|Argument|Description|
|--------|-----------|
|doi_prefix|DOI prefix used to get suffixes|
|mailto|contanct email address for the User-Agent header|


### Optional Arguments
|Flag|Description|
|----|-----------|
|-h, --help|show this help message and exit|
|-d DOI, --doi DOI|JSON output file for DOI|
|-c CACHE, --cache CACHE|output folder to cache results|
|-l LOG, --log LOG|output file for log|
|-v, -vv|increase output verbosity|
|--info|set output verbosity to 1 (INFO)|
|--debug|set output verbosity to 2 (DEBUG)|
|--verbosity {0,1,2}|set output verbosity|

## Library Usage
```
import app.doi_agency.datacite
```
## Development Usage

1. Configure environment variables for use **only in local development**

   - Create `.env` file in project root directory
   - For example configuration see `env.example`
   - All environment variables in `env.example` are required except `ROOT_PATH` ([for more infomation see Production Usage](#production-usage))
   - **Never** commit the `.env` file
   - Environment variables and their types are specified in the Pydantic model `ConfigApp Model` in `app/config.py`
     - `ConfigAppModel` should be updated as needed because it used for validation

2. Create a new virtual environment, activate it, and install dependencies from `requirements.txt`:

   ```bash
    pip install virtualenv
    python -m venv <virtual-environment-name>
    <virtual-environment-name>/Scripts/activate
    python -m pip install -r requirements.txt
   ```

3. Run the FastAPI server:

   ```bash
   uvicorn app.main:app --port 8000 --reload
   ```

   Or alternatively:

   ```bash
   fastapi dev app/main.py --reload
   ```

4. Access local server at: http://127.0.0.1:8000

