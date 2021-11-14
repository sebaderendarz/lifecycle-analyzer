# Machine lifecycle analyzer  

### Description
On-premise software. One can use this app by running a command `python analyzer.py` or create an installer.

****

### How to use

Press `Upload Data` button and select file containing data to be analyzed. `csv` and `xslx` formats supported.  

Data must be in exact format. 3 columns. First row as a header with the same fields' names as in sample files.  
In case of `csv`, fields in one row must be separated by semicolon. Check folder `samples` to get an overview.  

Program will automatically analyze selected data and display Weibull and Kaplan-Meier analysis results on charts.  
What is more, K and λ Weibull analysis parameters will be displayed.  

User can adjust theme, chart animations and legend alignment.  

****

### Dependencies
* PyQt5
* PyQtChart
* openpyxl

****

### How to create a Windows installer  
https://build-system.fman.io/pyqt-exe-creation/
