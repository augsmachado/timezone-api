import time
import json
from tracemalloc import start
import yaml

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
	title="Timestamp Utility API",
	version="1.0.0",
	description="API for status and timestamp conversion"
)

start_time = time.time()

# Allow CORS for all origins (optional, for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

locations = {
	"africa": {
		"min_latitude": 00,
		"max_latitude": 38,
		"min_longitude": -25,
		"max_longitude": 60,
	},
	"america": {
		"min_latitude": -55,
		"max_latitude": 72,
		"min_longitude": -170,
		"max_longitude": -30
	},
	"antarctica": {
		"min_latitude": -55,
		"max_latitude": 72,
		"min_longitude": -170,
		"max_longitude": -30
    },
	"asia": {
		"min_latitude": -55,
		"max_latitude": 72,
		"min_longitude": -170,
		"max_longitude": -30
	},
	"atlantic": {
		"min_latitude": -55,
		"max_latitude": 72,
		"min_longitude": -170,
		"max_longitude": -30
	},
	"australia": {
		"min_latitude": -55,
		"max_latitude": 72,
		"min_longitude": -170,
		"max_longitude": -30
	},
	"europe": {
		"min_latitude": 35,
		"max_latitude": 72,
		"min_longitude": -30,
		"max_longitude": 60
	},
	"indian": {
		"min_latitude": -55,
		"max_latitude": 72,
		"min_longitude": -170,
		"max_longitude": -30
	},
	"pacific": {
		"min_latitude": -55,
		"max_latitude": 72,
		"min_longitude": -170,
		"max_longitude": -30
	}
}


@app.get("/status")
def status():
	uptime = int(time.time() - start_time)
	return {
		"msg": "API status 🚀",
		"name": "timestamp-api",
		"version": app.version,
		"uptime": uptime,
	}


