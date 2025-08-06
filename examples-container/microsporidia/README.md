## Demonstrates how to run example.py in the container platform or COMPS platform

### Prerequisites:
- Install docker when running in container platform
- Create a virtual environment
- Activate the virtual environment
- Install emodpy-malaria and dependencies
- Install idmtools_platform_container and dependencies
  ```pip install -r requirements_container.txt```
- Check pip installation with pip list
- 

### Run example in local with container platform: 
  - Edit example.py to the line with     
    ```selected_platform = "Container"```
  - ```python example.py```

  - View running status:
    - idmtools container status <experiment_id>
  - View the output in the local job directory which you can find in console output while running the example.py
  - Optionally view the same output in the Docker container:
    - User can find container ID from console output and use the following command to view the output:
    ```bash
        docker exec -it <container_id> bash
        cd /home/container-data/<suite_dir>/<experiment_dir>/<simulation_dir>
    ```