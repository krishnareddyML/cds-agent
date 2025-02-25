# CDS-Agent
## Overview

The `cds-agent` project is designed to check Clinical Decision Support System (CDSS) rules sent by the EHR project against given patient data. This is achieved using the PydantAI Agent framework and local or external LLM (Large Language Model) models. The primary goal is to evaluate user free text queries and verify them using LLM Agents without the need to write any programmatic rules.

## Installation
To install the `cds-agent`, follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/krishnareddyML/cds-agent.git
    cd cdss-agent
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Run the application:
    ```sh
    uvicorn app.main:app --host=localhost --port=8003 --reload
    ```

## Features

- Can be integrate with EHR projects
- Utilizes PydanticAI Agent framework
- Supports both local and external LLM models
- Processes user free text queries
- No need for programmatic rule writing

## Usage

To use the `cdss-agent`, run the following command:

```sh
uvicorn app.main:app --host=localhost --port=8001 --reload
```
## From Postman call API
```sh
curl --location 'http://localhost:8003/cdsagent/run' \
--header 'Content-Type: application/json' \
--data '{
  "visitId": "75865",
  "cdssQuery": "is patient WBC > 10 and age >40",
  "modelName": "DiagnosticModelV1"
}'
```
## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.
