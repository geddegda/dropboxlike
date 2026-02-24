import os
import fastapi, uvicorn
import datetime
import secure, apikeys
from starlette.middleware.base import BaseHTTPMiddleware
from time import time

app = fastapi.FastAPI()


##### below is boiler plate and may not be necesary if rate limiting from nginx instead #############

request_counts = {}
RATE_LIMIT = 2  # Max 5 requests
TIME_WINDOW = 10  # Per 60 seconds

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: fastapi.Request, call_next):
        client_ip = request.client.host
        current_time = time()

        if client_ip in request_counts:
            request_times = request_counts[client_ip]

            # Remove outdated requests outside the time window
            request_counts[client_ip] = [
                timestamp for timestamp in request_times if current_time - timestamp < TIME_WINDOW
            ]

            if len(request_counts[client_ip]) >= RATE_LIMIT:
                raise fastapi.HTTPException(status_code=429, detail="Too Many Requests")

        # Add current request timestamp
        request_counts.setdefault(client_ip, []).append(current_time)

        # Proceed to the next middleware or endpoint
        response = await call_next(request)
        return response

# Add the middleware to the FastAPI app
app.add_middleware(RateLimitMiddleware)

##### above is boiler plate and may not be necesary if rate limiting from nginx instead #############

FOLDER ='/var/dropboxlike_temp'

@app.get("/")
def read_root():
    return {"is_it_up": f"yes at {datetime.datetime.now()}"}

#this is the command to test it: curl -H 'x-api-key: 9d207bf0-10f5-4d8f-a479-22gfdgfdgf555444eee238d1' --form file='@joseph.txt' http://localhost:8000/upload

@app.post("/upload")
def uploadfile(file: fastapi.UploadFile, api_key: str = fastapi.Security(secure.get_api_key)):
	try:
		file_path = f"/var/dropboxlike_temp/{file.filename}"
		with open(file_path, "wb") as f:
			f.write(file.file.read())
		return {"message": f"File saved OK at {datetime.datetime.now()}"}
	except Exception as e:
		return {"message": "An issue happened"}

#this is the command to test it: curl -H 'x-api-key: 9d207bf0-10f5-4d8f-a479-22gfdgfdgf555444eee238d1' -X DELETE http://localhost:8000/delete_files?file=joseph.txt

@app.delete("/delete_files")
def delete_file_in_folder(file: str, api_key: str = fastapi.Security(secure.get_api_key)):
	try:
		os.remove(f"{FOLDER}/{file}")
		return {"message": f"File deleted OK at {datetime.datetime.now()}"}
	except FileNotFoundError:
		return {"message": "File to delete does not exist"}
  
#this is the command to test it: curl -H 'x-api-key: 9d207bf0-10f5-4d8f-a479-22gfdgfdgf555444eee238d1' -X GET http://localhost:8000/list_files

@app.get("/list_files")
def list_files_in_folder(api_key: str = fastapi.Security(secure.get_api_key)):
	return {"files": os.listdir(FOLDER), "datetime": f"{datetime.datetime.now()}"}
	
if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)
