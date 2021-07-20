# FPL Extract
 
 Extract FPL Data with some data manipulation and then data is uploaded to google sheets. 

 The data is expected to come through in a JSON format and then from there we convert the JSON to Dataframes using the panda library. 
 
 After the data frame is created we filter out the columns we do not want. Then some data manipulations is done so we can have a better understanding of the data provided as well to see some extra information. 

 An upload to Google sheets is then done. This part requires pprerequisite work to get the credentials and then to be able to upload to Google sheets. After obtaining the credentials and creating a blank Google sheet we can upload our data frames to Google sheets. 

 We also create a few plots so we can see and visualise the data better. Each figure created is for each postion provided from FPL data, with each sub-plot in the figures having a scatter graph and a line graph.   