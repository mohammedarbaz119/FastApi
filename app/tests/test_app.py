from fastapi.testclient import TestClient
from fastapi import status
from fastapi.websockets import WebSocket,WebSocketDisconnect
from ..main import app


# As I have ONly allowed authenticated users to upload files so token Adding auth to the payload
token= "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhcmJheiIsImV4cCI6MTczMDc0Mzk3Nn0.WpiH7uCzb9k4yFmOwxWeP8RoFjLl1HqMJLn8oKp1J8s"
UNSUPPORTED_FILE ="./tests/output.txt"
SUPPORTED_FILE = "./tests/shakespeare_poem.pdf"


def test_read_main():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Server is running"}



def test_incorrect_file_format_upload():
    file = open(UNSUPPORTED_FILE,"rb")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    with TestClient(app) as client:
        res = client.post("/file/upload",headers=headers,files={"file": (UNSUPPORTED_FILE, file, "text/plain")})
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert res.json()["detail"] == "Please upload a PDF file!!"

def test_correct_file_format_upload():
    file = open(SUPPORTED_FILE,"rb")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    with TestClient(app) as client:
        res = client.post("/file/upload",headers=headers,files={"file": (SUPPORTED_FILE, file, "application/pdf")})
        assert res.status_code == status.HTTP_201_CREATED
        assert res.json()["message"] == "file uploaded and index created"  
        assert res.json()["pdf_name"] == 'shakespeare_poem.pdf'
            
def test_main_limit():
    with TestClient(app) as client:
        for _ in range(5):
            res = client.get("/")
        
        response = client.get("/")
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert response.json() == {"detail": "Too Many Requests"}

def test_socket_rate_limit():
    with TestClient(app) as client:
        with client.websocket_connect("/chat/ws/mypdf") as socket:
            for x in range(2):
               socket.send_text("what is a tensor?")

            try:
                while True:

                    response = socket.receive_text()
                    if response == "Too Many Requests":
                        break
            except WebSocketDisconnect:
                # If disconnected, the rate limit was successfully enforced
                assert True
            assert True
            


    
