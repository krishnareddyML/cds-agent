# cdss-agent
## Overview

The `cdss-agent` project is designed to check Clinical Decision Support System (CDSS) rules sent by the Imperium Falcon EHR project against given patient data. This is achieved using the PydantAI Agent framework and local or external LLM (Large Language Model) models. The primary goal is to evaluate user free text queries and verify them using LLM without the need to write any programmatic rules.

## Features

- Integration with Imperium Falcon EHR project
- Utilizes PydantAI Agent framework
- Supports both local and external LLM models
- Processes user free text queries
- No need for programmatic rule writing

## Usage

To use the `cdss-agent`, run the following command:

uvicorn app.main:app --host=192.168.20.95 --port=8001 --reload #dev
uvicorn app.main:app --host=192.168.20.87 --port=8001 --reload

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.
