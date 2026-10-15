async def start_sandbox(sandbox_executor):
    print("🚀 Starting E2B Secure Cloud Sandbox...")
    await sandbox_executor.start()
    print("✅ E2B Sandbox Started Successfully")

async def stop_sandbox(sandbox_executor):
    print("🛑 Stopping E2B Cloud Sandbox...")
    await sandbox_executor.stop()
    print("✅ E2B Sandbox Stopped Successfully")