# moveContainer
CloudVision Portal Move Container

# Description
This script can be used to move the specified container, its subcontainers and the devices under these containers to the target container with the same tree hierarchy.

In the first run, it should be run with "--suffixremove n" option. It then creates the containers with "_temp" suffix and deletes the original containers. At this stage bunch of move tasks will be created on CVP and needs to be run via a change control.

In the second run, it should be run with "--suffixremove y" option. It then creates the containers with original container names and deletes the temporary containers. At this stage bunch of move tasks will be created on CVP and needs to be run via a change control.

# Limitations
Although the script copies the configlet builders attached to containers, it does not run and generate them. This step should be done manually afterwards.

The script does not handle image bundles applied to containers.

# Example usage
python3 moveContainer.py --username cvpadmin --cvpIP 10.0.0.1 --containertobemoved Leafs --targetcontainer POD-1 --suffixremove n
python3 moveContainer.py --username cvpadmin --cvpIP 10.0.0.1 --containertobemoved Leafs_temp --targetcontainer POD-1 --suffixremove y

