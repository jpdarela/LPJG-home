import json
import platform


ins_name = "GLDAS_PWS.ins"

insfile_home = f"/home/jpdarela/guess/ins/{ins_name}"
insfile_cluster = f"/dss/dsshome1/lxc0F/ge83bol2/dss/ins/{ins_name}"


# Open the file for reading
with open('./guess4.1_hydraulics/.vscode/settings.json', 'r') as file:
    # Load its contents and parse the JSON
    launch_json = json.load(file)


if platform.node() == "curisco":
    launch_json["insfile"] = insfile_home
else:
    launch_json["insfile"] = insfile_cluster


# write file
with open('./guess4.1_hydraulics/.vscode/settings.json', 'w') as file:
    # Load its contents and parse the JSON
    json.dump(launch_json, file, indent=4)

