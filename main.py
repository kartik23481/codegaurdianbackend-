import os
import json
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Team and Sandbox imports
from team.DSA_Solving_Team import get_dsa_solver_team_and_docker
from config.sandbox_utils import start_sandbox, stop_sandbox
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult

app = FastAPI(title="CodeGuardian AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SolveRequest(BaseModel):
    task: str

async def autogen_stream_generator(task: str):
    """
    Executes AutoGen and streams resilient Server-Sent Events (SSE).
    """
    dsa_solver_team, e2b_sandbox = await get_dsa_solver_team_and_docker()
    await start_sandbox(e2b_sandbox)

    try:
        async for message in dsa_solver_team.run_stream(task=task):
            payload = None

            if isinstance(message, TaskResult):
                # Extract solution.py before tearing down the sandbox
                if e2b_sandbox and getattr(e2b_sandbox, "sandbox", None):
                    try:
                        # 🚨 CORRECTED: Changed .filesystem to .files
                        saved_code = await e2b_sandbox.sandbox.files.read("solution.py")
                        
                        with open("solution.py", "w", encoding="utf-8") as f:
                            f.write(saved_code)
                        print(" Successfully extracted solution.py from E2B Sandbox.")
                    except Exception as extraction_err:
                        print(f" Failed to extract solution.py: {extraction_err}")

                payload = {
                    "type": "stop",
                    "reason": getattr(message, "stop_reason", "Completed")
                }

            elif isinstance(message, TextMessage):
                payload = {
                    "type": "message",
                    "source": message.source,
                    "content": message.content
                }

            elif hasattr(message, "content") and isinstance(message.content, str) and message.content.strip():
                # Fallback for other AutoGen text-bearing message classes
                source_name = getattr(message, "source", "SYSTEM")
                payload = {
                    "type": "message",
                    "source": str(source_name),
                    "content": message.content
                }

            if payload:
                # Ensure no raw linebreaks break the SSE event format
                serialized = json.dumps(payload, ensure_ascii=False)
                yield f"data: {serialized}\n\n"

    except Exception as e:
        err_payload = json.dumps({"type": "error", "content": str(e)}, ensure_ascii=False)
        yield f"data: {err_payload}\n\n"

    finally:
        await stop_sandbox(e2b_sandbox)

@app.post("/api/solve")
async def solve_dsa_problem(request: SolveRequest):
    return StreamingResponse(
        autogen_stream_generator(request.task),
        media_type="text/event-stream"
    )

@app.get("/api/solution")
def get_saved_solution():
    try:
        with open("solution.py", "r", encoding="utf-8") as file:
            return {"success": True, "code": file.read()}
    except FileNotFoundError:
        return {"success": False, "error": "solution.py file not found on the server."}

@app.get("/")
def health_check():
    return {"status": "alive", "service": "CodeGuardian Backend"}

# if __name__ == "__main__":
#     import uvicorn
#     # IMPORTANT: reload=False prevents Uvicorn from aborting the stream when solution.py is written
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    import uvicorn
    import os
    # Render assigns a port dynamically. Default to 8000 for local testing.
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)