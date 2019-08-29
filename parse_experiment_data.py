import csv
import matplotlib.pyplot as plt

filename = "raw_unparsed_experiment_data.txt"

# csv data for runtime experiment
csv_data_1 = [["Function Name", "Number of nodes", "Average of 3 runs"]]
# csv data for memory consumption experiment
csv_data_2 = [["Number of nodes", "Average of 3 runs"]]


# In addition to the csv files we also want to create some graphs
# the x axis is the same for both graphs
x = []
y_dec_1 = []
y_dec_2 = []
y_mem = []

with open(filename) as f:
    line = f.readline()
    run_times_decrypt_v1 = []
    run_times_decrypt_v2 = []
    mem_consumptions = []
    node_num = 0
    while line:
        split_line = line.strip().split(" ")
        first_word = split_line[0]
        # check if start of new input
        if first_word == "Running":
            node_num = int(split_line[3])
        elif first_word == "decrypt_data_v1":
            run_times_decrypt_v1.append(float(split_line[3]))
        elif first_word == "decrypt_data_v2":
            run_times_decrypt_v2.append(float(split_line[3]))
        elif first_word == "Size":
            mem_consumptions.append(int(split_line[5]))
        elif first_word == "Ending":
            # calc averages for runtimes
            average_decrypt_v1 = sum(run_times_decrypt_v1) / len(run_times_decrypt_v1)
            average_decrypt_v2 = sum(run_times_decrypt_v2) / len(run_times_decrypt_v2)
            # line for first func
            csv_data_1.append(["decrypt_data_v1", node_num, average_decrypt_v1])
            csv_data_1.append(["decrypt_data_v2", node_num, average_decrypt_v2])
            # decryption graph
            y_dec_1.append(average_decrypt_v1)
            y_dec_2.append(average_decrypt_v2)
            # calc averages for mem consumption
            average_mem_consumption = sum(mem_consumptions) / len(mem_consumptions)
            # data for second experiment
            csv_data_2.append([node_num, average_mem_consumption])
            # nodes for x axis that is used in both graphs
            x.append(node_num)
            # mem graph
            y_mem.append(average_mem_consumption)
            # reset runtimes
            run_times_decrypt_v1 = []
            run_times_decrypt_v2 = []
            # reset mem_consumptions
            mem_consumptions = []

        # read the next line if there is one
        line = f.readline()

with open("runtime_experiment_data.csv", "w", newline="") as csv_file_1:
    writer = csv.writer(csv_file_1)
    writer.writerows(csv_data_1)

with open("memory_experiment_data.csv", "w", newline="") as csv_file_2:
    writer = csv.writer(csv_file_2)
    writer.writerows(csv_data_2)

# create decryption graph
plt.figure(1)
line_dec_1 = plt.plot(x, y_dec_1, marker="o", label="Algorithm 2")
line_dec_2 = plt.plot(x, y_dec_2, marker="o", label="Algorithm 3")
plt.title("Runtimes For Data Decryption Algorithms")
plt.ylabel("Seconds")
plt.xlabel("Nodes")
plt.legend()
plt.savefig("runtime_experiment_graph.pdf", bbox_inches="tight")

# create mem graph
plt.figure(2)
plt.plot(x, y_mem, marker="o")
plt.title("Memory Consumption")
plt.ylabel("Bytes")
plt.xlabel("Nodes")
plt.savefig("memory_experiment_graph.pdf", bbox_inches="tight")
