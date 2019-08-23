import csv

filename = "raw_unparsed_experiment_data.txt"

# csv data for runtime experiment
csv_data_1 = [["Function Name", "Number of nodes", "Average of 3 runs"]]
# csv data for memory consumption experiment
csv_data_2 = [["Number of nodes", "Average of 3 runs"]]

with open(filename) as f:
    line = f.readline()
    run_times_decrypt_v1 = []
    run_times_decrypt_v2 = []
    mem_consumptions = []
    node_num = 0
    while line:
        # check if start of new input
        if line.startswith("Running"):
            split_line = line.split(" ")
            node_num = int(split_line[3])
        if line.startswith("decrypt_data_v1"):
            split_line = line.split(" ")
            run_times_decrypt_v1.append(float(split_line[3]))
        if line.startswith("decrypt_data_v2"):
            split_line = line.split(" ")
            run_times_decrypt_v2.append(float(split_line[3]))
        if "@profile" in line:
            split_line = line.strip().split(" ")
            # get rid of spaces in between
            filtered_line = [x for x in split_line if x]
            mem_consumptions.append(float(filtered_line[1]))
        if line.startswith("Ending experiment"):
            # calc averages for runtimes
            average_decrypt_v1 = sum(run_times_decrypt_v1) / len(run_times_decrypt_v1)
            average_decrypt_v2 = sum(run_times_decrypt_v2) / len(run_times_decrypt_v2)
            # line for first func
            csv_data_1.append(["decrypt_data_v1", node_num, average_decrypt_v1])
            csv_data_1.append(["decrypt_data_v2", node_num, average_decrypt_v2])
            # calc averages for mem consumption
            average_mem_consumption = sum(mem_consumptions) / len(mem_consumptions)
            # data for second experiment
            csv_data_2.append([node_num, average_mem_consumption])
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