DataCite Export
===============

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

