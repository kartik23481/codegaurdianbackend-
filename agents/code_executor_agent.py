# from autogen_agentchat.agents import CodeExecutorAgent 
# from config.docker_container import get_docker_container

# def get_code_executor_agent():
#     # getting the docker contaier
#     docker = get_docker_container()
#     # Define the agent which runs the code in the docker container
#     code_executor_agent = CodeExecutorAgent(
#         name= 'CODE_EXECUTOR_AGENT',
#         code_executor=docker
#     )
#     return code_executor_agent,docker




from autogen_agentchat.agents import CodeExecutorAgent 
from config.e2b_sandbox import get_e2b_sandbox

def get_code_executor_agent():
    # Get the E2B Cloud Sandbox
    e2b_sandbox = get_e2b_sandbox()
    
    # Define the agent which runs the code in the cloud sandbox
    code_executor_agent = CodeExecutorAgent(
        name='CODE_EXECUTOR_AGENT',
        code_executor=e2b_sandbox
    )
    return code_executor_agent, e2b_sandbox