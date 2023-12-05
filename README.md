git clone the repository
cd repository_directory
poetry shell
poetry install
cd app
uvicorn main:app --reload
