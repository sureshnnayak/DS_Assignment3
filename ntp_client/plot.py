from matplotlib import pyplot
import json
import sys
import pathlib
import os


def plot(total_delay, total_offset, delay, offset, name, src_dir):
    pyplot.plot([i for i in range(0,len(total_delay))], total_delay, label='delay')
    pyplot.plot([i for i in range(0,len(total_offset))], total_offset, label='offset')
    pyplot.plot([i*8 for i in range(0,len(delay))], delay, label='delay_0')
    pyplot.plot([i*8 for i in range(0,len(offset))], offset, label='offset_0')
    pyplot.xlabel("Messages")
    pyplot.ylabel("Delay/Offset")
    pyplot.title(name)    
    pyplot.legend()
    pyplot.savefig(f"{src_dir}/graphs/Graph_{name}.png")
    #pyplot.show()

  
if __name__ == "__main__":
    src_dir = pathlib.Path(__file__).parent.resolve()
    filepath = os.getenv("FILE",f"{src_dir}/logs/plotting_data_localhost.json")
    server_type = os.getenv("SERVER","Local_NTP_Server")
    with open(filepath,"r") as f:
        data = json.loads(f.read())
        total_delay = data["total_delay"]
        total_offset = data["total_offset"]
        delay = data["delay0"]
        offset = data["offset0"]
    plot(total_delay, total_offset, delay, offset, server_type,src_dir)