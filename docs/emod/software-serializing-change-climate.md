# Changing serialized climate parameters



Climate data can be changed as it is not serialized.  However, if the serialized file was created
with weather data files, then it is best practices to save the file such that when the simulation is
restarted the time of the year remains the same.  For example, if you saved the file at the end of
the dry season and start the simulation at the beginning of the dry season, the pressure on the
vectors will be twice as long as normal and could impact results.

Note that currently only vector and malaria simulations utilize climate files.

There are couple ways to do this:

# Always save your serialized files on 365 day intervals.  This way you know that the first day of the simulation that is reading from the file will start on January 1st.
# Use the configuration parameter **Start_Time** to have the scenario start the day after the simulation was serialized.  This can allow you to start right where you left off.


## Editable climate parameters


* **Climate_Model**
* **Climate_Update_Resolution**
* **Enable_Climate_Stochasticity**
* **Enable_Rainfall_Stochasticity**
* **Air_Temperature_Variance**
* **Land_Temperature_Variance**
* **Relative_Humidity_Variance**

### **Climate_Model** = CLIMATE_CONSTANT


* **Base_Air_Temperature**
* **Base_Land_Temperature**
* **Base_Rainfall**
* **Base_Relative_Humidity**

### **Climate_Model** = CLIMATE_BY_DATA


* **Air_Temperature_Filename**
* **Land_Temperature_Filename**
* **Rainfall_Filename**
* **Relative_Humidity_Filename**
* **Air_Temperature_Offset**
* **Land_Temperature_Offset**
* **Rainfall_Scale_Factor**
* **Relative_Humidity_Scale_Factor**

### **Climate_Model** = CLIMATE_KOPPEN


* **Koppen_Filename**