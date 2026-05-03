# Changing reports in serialized simulations



Reports can be changed as they are not serialized.  If a report has a channel that involves
accumulating data over a period of time, it will start fresh with the new realization
from the de-serialized data.

The following parameters can be changed:

* **Enable_Default_Reporting**
* **Enable_Demographics_Reporting**
* **Enable_Property_Output**
* **Enable_Spatial_Output**
* **Report_Event_Recorder**
* **Enable_Vector_Species_Report**

The following report parameters can be changed; their new values will only impact the reports
in new realizations from the deserialized data:

* **Report_Detection_Threshold_Blood_Smear_Parasites**
* **Report_Detection_Threshold_Blood_Smear_Gametocytes**
* **Report_Detection_Threshold_PCR_Parasites**
* **Report_Detection_Threshold_PCR_Gametocytes**
* **Report_Detection_Threshold_PfHRP2**
* **Report_Detection_Threshold_True_Parasite_Density**
* **Report_Detection_Threshold_Fever**
* **Report_Parasite_Smear_Sensitivity**
* **Report_Gametocyte_Smear_Sensitivity**