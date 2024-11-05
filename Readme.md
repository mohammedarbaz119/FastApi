# FastAPI Project Setup Guide

This guide walks you through setting up a FastAPI project, including installing dependencies from `requirements.txt`, configuring environment variables, and running the application in both development and production modes.

## Prerequisites

1. **Python**: Ensure Python 3.8+ is installed on your system.
2. **Virtual Environment** (recommended): Set up a virtual environment for isolating dependencies.

## Step 1: Clone the Repository

If your FastAPI project is hosted on a Git repository, clone it using:

```bash
git clone <repository-url>
cd <project-folder>
```

## Step 2: Install Dependencies

Make sure you are in the project directory, then install the required dependencies from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Step 3: Set Up Environment Variables

To securely store sensitive information, create a `.env` file in the project root directory. Copy the following environment variables into the `.env` file and replace the placeholder values with your actual secrets.

```plaintext
API_KEY=""
CLOUDFLARE_TOKEN=""
CLOUDFLARE_ACCOUNT_ID=""
MONGO_CONN=""
DB_NAME="fastapi"
COLLECTION_NAME="userpdfs"
VECTOR_INDEX_NAME="fast_search"
API_BASE_URL="https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/"
SECRET_KEY=""
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=""
```

> **Note:** Be sure to replace `{CLOUDFLARE_ACCOUNT_ID}` with the actual Cloudflare Account ID.

### Explanation of Environment Variables:

- **API_KEY**: API key for external services (e.g., Google API).
- **CLOUDFLARE_TOKEN**: Token for accessing Cloudflare API.
- **CLOUDFLARE_ACCOUNT_ID**: Cloudflare Account ID for making requests to the llm (using custom LLM).
- **MONGO_CONN**: MongoDB connection URI.
- **DB_NAME**: Name of the MongoDB database.
- **COLLECTION_NAME**: Name of the MongoDB collection for storing PDFs.
- **VECTOR_INDEX_NAME**: Name of the vector index for search functionality.
- **API_BASE_URL**: Base URL for Cloudflare API.
- **SECRET_KEY**: Secret key for signing JWT tokens.
- **ALGORITHM**: Algorithm used for JWT encoding.
- **ACCESS_TOKEN_EXPIRE_MINUTES**: Expiration time for access tokens in minutes.
- **REDIS_URL**: Redis server URL for caching and storing session data.

## Step 4: Running the FastAPI Application

### Development Mode

To run the application in development mode with hot reloading, use:

```bash
fastapi dev main.py
```

This will automatically reload the server on any file changes, which is useful for development.

### Production Mode

For production, it’s recommended to use fastapi run. Run the following command:

```bash
fastapi run main.py
```

This command starts the application for production use

---

### Additional Notes

- **.gitignore**: Ensure your `.env` file is listed in `.gitignore` to avoid committing sensitive information to version control.


server will be running on port 8000
By following these steps, you will have a properly configured and securely running FastAPI project.