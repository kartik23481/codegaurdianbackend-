from autogen_core.code_executor import CodeExecutor, CodeBlock, CodeResult
from e2b_code_interpreter import AsyncSandbox
from config.constants import TIMEOUT
import asyncio

class E2BCommandLineCodeExecutor(CodeExecutor):
    def __init__(self, timeout: int = TIMEOUT):
        self.timeout = timeout
        self.sandbox = None

    async def start(self):
        """Initializes the secure E2B MicroVM in the cloud."""
        if not self.sandbox:
            self.sandbox = await AsyncSandbox.create()

    async def stop(self):
        """Kills the E2B MicroVM to free up resources."""
        if self.sandbox:
            await self.sandbox.kill()
            self.sandbox = None

    async def restart(self):
        """Restarts the E2B MicroVM (Required by AutoGen v0.4 Base Class)."""
        await self.stop()
        await self.start()

    async def execute_code_blocks(self, code_blocks: list[CodeBlock], cancellation_token: any) -> CodeResult:
        if not self.sandbox:
            await self.start()
            
        logs = ""
        has_error = False
        
        for block in code_blocks:
            try:
                # 1. PYTHON EXECUTION
                if block.language.lower() == "python":
                    execution = await self.sandbox.run_code(block.code, timeout=self.timeout)
                    
                    # FIX: Capture standard print() statements
                    if execution.logs and execution.logs.stdout:
                        logs += "".join(execution.logs.stdout) + "\n"
                        
                    # Capture Jupyter-style cell returns
                    if execution.text: 
                        logs += execution.text + "\n"
                        
                    # Capture Python runtime errors
                    if execution.error:
                        logs += f"ERROR:\n{execution.error.name}: {execution.error.value}\n{execution.error.traceback}\n"
                        has_error = True
                        
                # 2. C++ EXECUTION
                elif block.language.lower() in ["cpp", "c++"]:
                    await self.sandbox.filesystem.write("main.cpp", block.code)
                    process = await self.sandbox.commands.run(
                        "g++ main.cpp -o main_exec && ./main_exec", 
                        timeout=self.timeout
                    )
                    
                    if process.stdout: 
                        logs += process.stdout + "\n"
                    if process.stderr:
                        logs += f"ERROR:\n{process.stderr}\n"
                        has_error = True

                # 3. BASH EXECUTION
                elif block.language.lower() in ["bash", "sh"]:
                    process = await self.sandbox.commands.run(block.code, timeout=self.timeout)
                    if process.stdout: 
                        logs += process.stdout + "\n"
                    if process.stderr:
                        logs += f"ERROR:\n{process.stderr}\n"
                        has_error = True
                else:
                    logs += f"Unsupported language: {block.language}\n"
                    has_error = True
                    
            except Exception as e:
                logs += f"Sandbox Execution Exception: {str(e)}\n"
                has_error = True
                
            if has_error:
                break
                
        return CodeResult(output=logs.strip(), exit_code=1 if has_error else 0)

        
def get_e2b_sandbox():
    """Returns an instance of our custom E2B AutoGen executor."""
    sandbox_executor = E2BCommandLineCodeExecutor(timeout=TIMEOUT)
    return sandbox_executor