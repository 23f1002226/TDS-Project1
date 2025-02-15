import httpx
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import datetime
import os
import json

from base_logger import logger

from a1 import run_datagen_script
from a2 import format_file_with_prettier
from a3 import count_given_weekday_in_dates
from a4 import sort_contacts_file
from a5 import write_most_recent_log_first_lines
from a6 import extract_titles_from_markdown_files
from a7 import extract_sender_email
from a9 import get_similar_comments
from a8 import extract_numbers_from_image
from a10 import calculate_ticket_sales
from tools_a import tools
from common import OPENAI_API_URL, OPENAI_API_KEY, query_gpt

app = FastAPI()

@app.post("/run")
async def run_task(task: str):
    print(" " * 80)
    print("=" * 80)
    print(" " * 80)
    logger.info(f"[{now}]Task received:{task}")
    try:
        response = await query_gpt(
            task,
            tools,
            OPENAI_API_KEY=OPENAI_API_KEY,
            OPENAI_API_URL=OPENAI_API_URL + r"chat/completions",
        )

    except Exception as e:
        logger.error(f"Error occurred while querying GPT: {e}")
        raise HTTPException(status_code=404, detail="Error occurred while querying GPT")

    fname = response["name"]
    arguments = response["arguments"]
    arg_dict = json.loads(arguments)

    # print(f"Calling function: {fname}")
    # print(f"With the below arguments: {arg_dict = }")

    arg_dict_str = ", ".join([f"{k}='{v}'" for k, v in arg_dict.items()])
    print("-" * 80)
    logger.info(f"Calling function: {fname}({arg_dict_str})")

    try:
        fun = globals()[fname]
        await fun(**arg_dict)
    except Exception as e:
        logger.error(
            f"Error occurred while calling the function {fname}. Error is: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal Error occurred while running called the function",
        )
    print("-" * 80)
    return JSONResponse(content={"function": fname, "arguments": arg_dict})


from fastapi.responses import PlainTextResponse


@app.get("/read", response_class=PlainTextResponse)
async def read_file(path: str):
    print("-" * 80)
    from pathlib import Path

    file_path = Path(path)

    # Check if the file exists and is a file
    if not file_path.is_file():
        logger.error(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail="File not found")

    # Open the file and read its content
    try:
        with open(file_path, "r") as file:
            content = file.read()
        return content
    except Exception as e:
        logger.error(f"Exception from inside app.get('/read')")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    # logger.basicConfig(level="INFO", format="%(message)s\n")
    logger.debug(f"{OPENAI_API_KEY=}")

    uvicorn.run(app, port=8000)