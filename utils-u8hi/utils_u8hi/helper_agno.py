import os
from time import time 
from datetime import datetime
from agno.agent import Agent


def log_response(topic, resp_msg, model_id, ts_now, elapsed_sec, file_log="", to_print=True):
    if to_print:
        # print to console
        print(resp_msg)

    if not file_log:
        filename_without_ext = os.path.splitext(os.path.basename(__file__))[0]  # e.g., "script"
        file_log = f"{filename_without_ext}.log.md"

    # log Agent response
    with open(file_log, "a") as flog:
        flog.write("\n\n" + 50*"=" + "\n")
        flog.write(f"\n ## {topic} \n")
        flog.write(f"\n [{ts_now}] \n")
        flog.write("\n\n" + 50*"=" + "\n\n")
        flog.write(resp_msg)
        flog.write(f"\n\n[{model_id}] Completed in {elapsed_sec:.3f} sec")
        flog.write("\n\n" + 20*"=" + "\n")


def get_file_log(filename):
    filename_without_ext = os.path.splitext(os.path.basename(filename))[0]  # e.g., "script"
    return f"{filename_without_ext}.log.md" 

def invoke_agent(agent: Agent, topic : str, model_id: str = "", file_log : str = ""):
    if not topic.strip():
        return

    ts_now = str(datetime.now())

    ts_start = time()
    run_resp = agent.run(topic)
    ts_stop = time()

    elapsed_sec = ts_stop - ts_start
    resp_msg = run_resp.content

    log_response(
            topic, 
            resp_msg, 
            model_id, 
            ts_now, 
            elapsed_sec, 
            file_log = get_file_log(file_log),
        )
