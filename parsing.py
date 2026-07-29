import os, sys

class parser:
    def parsing(self):
        hubs: str = []
        hubmetadata: str = []
        connection: str = []
        connectionmetadata: str = []
        try:
            file_name = sys.argv[1]
            with open(file_name, "r") as data:
                for line in data:
                    lin = line.strip()
                    if "nb_drones" in lin:
                       nb_drones = lin.split(":")[1].strip()
                    if "start_hub" in lin:
                       hubs.append(lin.split()[1].strip())
                    if "end_hub" in lin:
                       hubs.append(lin.split()[1].strip())
                    if lin.startswith("hub"):
                        parts = lin.split()
                        hubs.append(parts[1])
                        if len(parts) > 4:
                            hubmetadata.append(parts[4].strip("[]"))
                        else:
                            hubmetadata.append(None)
                    if lin.startswith("connection"):
                        parts = lin.split()
                        connection.append(parts[1])
                        if len(parts) > 2:
                            connectionmetadata.append(parts[2].strip("[]"))
                        else:
                            connectionmetadata.append(None)
                print(hubmetadata)      
        except Exception as e:
            print(f"Error: '{e}'.")
b = parser()
b.parsing() 

