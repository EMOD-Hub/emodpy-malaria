## Demonstrates how to run a campaign sweep in the container platform or COMPS platform

### Prerequisites:
- Install docker when running in container platform
- Create a virtual environment
- Activate the virtual environment
- Install emodpy-malaria and dependencies
- Install idmtools_platform_container and dependencies
  ```pip install -r requirements_container.txt```
- Check pip installation with pip list

### Run example.py in local computer with container platform: 
   - Run example.py:
    ```python example.py```
   - View running status:
     ```idmtools container status <experiment_id>```
   - View the output in the local job directory which you can find in console output while running the example.py
     directory path: <job_directory>/<suite_dir>/<experiment_dir>/<simulation_dir>
     - View the output in the Docker container:
       User can find container ID from console output and use the following command to view the output:
     ```bash
        docker exec -it <container_id> bash
        ls -la /home/container-data/<suite_dir>/<experiment_dir>/<simulation_dir>
     ```
   - Optionally you can also change your simulation directory path with or without experiment name as prefix:
     Create idmtools.ini file in the same directory where example.py is located and add the following content:
     ```ini
     [COMMON]
     name_directory = True   # default value, if you want to add experiment name as prefix
     sim_name_directory  = False  # default value, if you want to add simulation name as prefix, set to True
     ```
     Note, in windows, there is limitation on the length of the path, so you need to keep the path length in mind while setting the above values. and also make sure overall job directory path length is less than 255 characters.


