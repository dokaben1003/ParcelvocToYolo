XML to YOLO Converter
This is a Python script designed to convert XML files, containing annotation information, into the YOLO format.

Key Features
Extract object annotation data from XML files.
Convert the extracted annotation data to the YOLO format.
Capture all unique class names and save them in classes.txt.
Usage
Install the required modules:
bash
Copy code
pip install lxml opencv-python
Execute the script:
bash
Copy code
python converter.py --xml_dir /path/to/xml/files --img_dir /path/to/image/files --yolo_dir /path/to/yolo/output --classes_txt_dir /path/to/classes_txt/output --error_dir /path/to/error/log
Arguments
--xml_dir: Absolute path to the directory containing XML files.
--img_dir: Absolute path to the directory containing image files.
--yolo_dir: Absolute path to the directory where the converted YOLO files will be saved.
--classes_txt_dir: Absolute path to the directory where the classes.txt file will be saved.
--error_dir: Absolute path to the directory where error logs will be stored.
Note
Image files and XML files are paired based on their filenames. Ensure that there is a corresponding image file for each XML file with the same name.
In case of errors, an error log named xmlfiles_with_no_paired.txt will be saved in the directory specified by error_dir.
