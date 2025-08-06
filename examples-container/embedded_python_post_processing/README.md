# Malaria_Sim Example with Embedded Python Post-Processing (EP4)

### Run example.py in container platform:
  - Run example.py:
    ```python example.py```
  - View running status:
    - idmtools container status <experiment_id>
  - View the output in the local job directory which you can find in console output while running the example.py
  - Optionally view the same output in the Docker container:
    - User can find container ID from console output and use the following command to view the output:
    ```bash
        docker exec -it <container_id> bash
        cd /home/container-data/<suite_dir>/<experiment_dir>/<simulation_dir>
    ```