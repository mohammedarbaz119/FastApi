
---

# FastAPI API Documentation

## Overview

This API provides endpoints for user authentication, file uploads, and listing available files. The API is designed with security and functionality in mind, using OAuth2 for token-based authorization.

---

## Authentication Endpoints

### Login For Access Token
- **Endpoint**: `POST /auth/login`
- **Description**: Authenticates a user and issues an access token upon successful login.
- **Request Body**:
  - `username` (string, required): The username of the user.
  - `password` (string, required): The user's password.
- **Response**:
  - `200 OK`: Returns an access token upon successful authentication.
  - `422 Validation Error`: If the request body fails validation.
- **Schema**: Returns a `Token` object with `access_token` and `token_type` fields.

### Register User
- **Endpoint**: `POST /auth/register/`
- **Description**: Registers a new user with the required details.
- **Request Body**:
  - `username` (string, required): Desired username for the new user.
  - `email` (string, required): Email address of the user.
  - `password` (string, required): Password for the new user.
- **Response**:
  - `200 OK`: Successfully registers the user.
  - `422 Validation Error`: If the request body fails validation.

---

## File Handling Endpoints

### Upload File
- **Endpoint**: `POST /file/upload/`
- **Description**: Allows authorized users to upload files to build indexes for pdf Question Answering. This endpoint requires OAuth2 token-based authorization.
- **Request Body**:
  - `file` (binary, required): The file to be uploaded.
- **Response**:
  - `200 OK`: File uploaded successfully.
  - `422 Validation Error`: If the file fails validation.
- **Security**: Requires an OAuth2 Bearer token in the authorization header.

### Get All Files (Paginated)
- **Endpoint**: `GET /file/files/{page}`
- **Description**: Lists all uploaded files with pagination support.
- **Path Parameters**:
  - `page` (integer, required): The page number to retrieve.
- **Query Parameters**:
  - `limit` (integer, optional, default = 1): The number of files per page.
- **Response**:
  - `200 OK`: Returns a paginated list of files.
  - `422 Validation Error`: If the request parameters fail validation.

---

## Root Endpoint

### Read Root
- **Endpoint**: `GET /`
- **Description**: A basic root endpoint for testing connectivity.
- **Response**:
  - `200 OK`: Returns a simple success message.

---

## Schemas

### Token
- **Fields**:
  - `access_token` (string, required): The issued access token.
  - `token_type` (string, required): The type of token issued, typically "bearer".

### UserForm
- **Fields**:
  - `username` (string, required): Username of the user.
  - `email` (string, required): Email address of the user.
  - `password` (string, required): Password of the user.

### Form
- **Fields**:
  - `username` (string, required): Username of the user.
  - `password` (string, required): Password of the user.

### HTTPValidationError
- **Fields**:
  - `detail` (array of `ValidationError`): List of validation errors.

### ValidationError
- **Fields**:
  - `loc` (array): The field(s) where the error occurred.
  - `msg` (string): The error message.
  - `type` (string): Type of error.

---

## Security Scheme

- **OAuth2PasswordBearer**:
  - **Type**: OAuth2
  - **Flow**: Password
  - **Token URL**: `/auth/login`
  - **Scopes**: No specific scopes required.

# WebSocket Chat API Documentation

This WebSocket API allows clients to establish a connection for real-time chat and receive responses from an LLM-based chatbot using context-specific data. Rate limiting is applied to manage request flow.

## WebSocket Endpoint

### `GET /ws/{filename}`

Initiates a WebSocket connection for real-time chat. This connection supports multiple concurrent clients, with each client having a unique session identified by a `sockid`.

- **URL Parameters**:
  - `filename` (str): The filename related to the context. This file will be used to filter the context applied in the chat.

- **Rate Limiting**: The endpoint allows 1 request every 20 seconds per connection to control request volume.

### Example Workflow

1. **Connect**:
   - Client establishes a WebSocket connection to `/ws/{filename}`.
   - Upon connection, a unique `sockid` is generated, and a chat engine is initialized using the `filename` context.

2. **Send Messages**:
   - Client sends a question or message as a string of text.
   - Server processes the request using the provided context, chat memory, and a specific LLM prompt template.

3. **Receive Responses**:
   - The server streams responses from the LLM, chunk by chunk, back to the client.
   - If there’s no relevant context, the model will respond: `"There was no context to answer the Question..."`.

4. **Rate Limit Exceeded**:
   - If rate limits are exceeded, the client receives `"Too Many Requests"` and is disconnected.

5. **Disconnect**:
   - When a client disconnects or rate limits are breached, all associated memory and session data are cleared.

### Response Examples

#### Success
- **Chunked Streaming Response**: The response is streamed chunk by chunk based on LLM processing.
  
#### No Context
- **No Context Found**: `"There was no context to answer the Question..."`

#### Rate Limit Exceeded
- **Error Message**: `"Too Many Requests"`

### Error Handling

- **WebSocketDisconnect**: Automatically clears session data and memory.
- **WebSocketException**: Sends `"Too Many Requests"` message if rate limits are breached.

---

### Technical Details

#### Dependencies and Components

- **Redis**: Manages Rate Limiting for Websockets messages and API
- **ConnectionManager**: Manages active connections, chat engines, and in-memory storage for each session.
- **RedisChatStore**: Stores chat history in Redis for session based context/persistent storage across.
- **Chat Engine**: LLM-driven chat engine with custom filters based on the `filename`.
- **Prompt Template**: Customized prompt template for question-answering using context.


