# from agents.code_executor_agent import get_code_executor_agent
# from agents.problem_solver_agent import get_problem_solver_agent
# from autogen_agentchat.teams import RoundRobinGroupChat
# from config.constants import TERMINATION_TEXT,MAX_TURNS
# from autogen_agentchat.conditions import TextMentionTermination

# async def get_dsa_solver_team_and_docker():
#     problem_solver_agent = get_problem_solver_agent()
#     code_executor_agent,docker = get_code_executor_agent()
#     TERMINATION_CONDITION = TextMentionTermination(TERMINATION_TEXT)

#     # Now configuring the team that solves the DSA problem
#     team = RoundRobinGroupChat(
#         participants = [
#             problem_solver_agent,
#             code_executor_agent
#         ],
#         termination_condition=TERMINATION_CONDITION,
#         max_turns = MAX_TURNS
#     )
#     await team.reset()
#     return team,docker




from agents.code_executor_agent import get_code_executor_agent
from agents.problem_solver_agent import get_problem_solver_agent
from agents.verifier_agent import get_verifier_agent  # NEW IMPORT
from autogen_agentchat.teams import RoundRobinGroupChat
from config.constants import TERMINATION_TEXT, MAX_TURNS
from autogen_agentchat.conditions import TextMentionTermination

async def get_dsa_solver_team_and_docker():
    problem_solver_agent = get_problem_solver_agent()
    # code_executor_agent, docker = get_code_executor_agent()
    code_executor_agent, e2b_sandbox = get_code_executor_agent()
    verifier_agent = get_verifier_agent()  # INITIALIZE NEW AGENT
    
    TERMINATION_CONDITION = TextMentionTermination(TERMINATION_TEXT)

    # Now configuring the team that solves the DSA problem
    # ORDER IS STRICT: Solver writes code -> Executor runs it -> Verifier checks it
    team = RoundRobinGroupChat(
        participants=[
            problem_solver_agent,
            code_executor_agent,
            verifier_agent
        ],
        termination_condition=TERMINATION_CONDITION,
        max_turns=MAX_TURNS
    )
    
    await team.reset()
    # return team, docker
    return team, e2b_sandbox
