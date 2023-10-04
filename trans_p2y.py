import os
import cv2
from lxml import etree
from xml.etree import ElementTree
from glob import glob
import argparse

class GetDataFromXMLfile:
    def __init__(self, xmlfile_path):
        self.xmlfile_path = xmlfile_path
        self.xmlfile_datalists_list = []

    def get_datalists_list(self):
        """Parse the XML file and return the extracted data."""
        self.parse_xmlfile()
        return self.xmlfile_datalists_list

    def parse_xmlfile(self):
        """Parse the XML file and extract relevant data."""
        lxml_parser = etree.XMLParser(encoding='utf-8')
        xmltree = ElementTree.parse(self.xmlfile_path, parser=lxml_parser).getroot()

        for object in xmltree.findall('object'):
            xmlfile_datalist = []
            class_name = object.find('name').text
            xmlfile_datalist.append(class_name)
            bndbox = object.find("bndbox")
            xmlfile_datalist.append(bndbox)
            self.xmlfile_datalists_list.append(xmlfile_datalist)

        img_filename = xmltree.find('filename').text
        self.add_data_to_datalist(img_filename)

    def add_data_to_datalist(self, img_filename):
        """Convert bndbox XML elements to coordinate tuples and add to the data list."""
        for xmlfile_datalist in self.xmlfile_datalists_list:
            xmin = float(xmlfile_datalist[1].find('xmin').text)
            ymin = float(xmlfile_datalist[1].find('ymin').text)
            xmax = float(xmlfile_datalist[1].find('xmax').text)
            ymax = float(xmlfile_datalist[1].find('ymax').text)
            bndbox_coordinates_list = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
            xmlfile_datalist[1] = bndbox_coordinates_list

        self.xmlfile_datalists_list.append(img_filename)
        self.xmlfile_datalists_list.append(self.xmlfile_path)


class CreateYOLOfile:
    def __init__(self, xmlfile_datalists_list, classes_list, args):
        self.xmlfile_datalists_list = xmlfile_datalists_list
        self.args = args
        self.xmlfile_path = self.xmlfile_datalists_list.pop()
        self.img_filename = self.xmlfile_datalists_list.pop()
        self.yolofile_path = self.args.yolo_dir + self.img_filename.rsplit('.', 1)[0] + '.txt'

        self.classes_list = classes_list
        try:
            (self.img_height, self.img_width, _) = cv2.imread(args.img_dir + self.img_filename).shape
            self.create_yolofile()
        except:
            with open(args.error_dir+'xmlfiles_with_no_paired.txt', 'a') as f:
                f.write(os.path.basename(self.xmlfile_path)+'\n')

    def create_yolofile(self):
        """Create YOLO format file from XML extracted data."""
        with open(self.yolofile_path, 'w') as f:  
            for xmlfile_datalist in self.xmlfile_datalists_list:
                yolo_datalist = self.convert_xml_to_yolo_format(xmlfile_datalist)
                f.write("%d %.06f %.06f %.06f %.06f\n" % (yolo_datalist[0], yolo_datalist[1], yolo_datalist[2], yolo_datalist[3], yolo_datalist[4]))

    def convert_xml_to_yolo_format(self, xmlfile_datalist):
        """Convert XML data format to YOLO data format."""
        class_name = xmlfile_datalist[0]
        self.add_class_to_classeslist(class_name)
        bndbox_coordinates_list = xmlfile_datalist[1]
        coordinates_min = bndbox_coordinates_list[0]
        coordinates_max = bndbox_coordinates_list[2]

        class_id = self.classes_list.index(class_name)
        yolo_xcen = float((coordinates_min[0] + coordinates_max[0])) / 2 / self.img_width
        yolo_ycen = float((coordinates_min[1] + coordinates_max[1])) / 2 / self.img_height
        yolo_width = float((coordinates_max[0] - coordinates_min[0])) / self.img_width
        yolo_height = float((coordinates_max[1] - coordinates_min[1])) / self.img_height
        yolo_datalist = [class_id, yolo_xcen, yolo_ycen, yolo_width, yolo_height]

        return yolo_datalist

    def add_class_to_classeslist(self, class_name):
        """Add a new class to the classes list if it's not already present."""
        if class_name not in self.classes_list:
            self.classes_list.append(class_name)

class CreateClasssesfile:
    def __init__(self, classes_list, args):
        self.classes_list = classes_list
        self.args = args

    def create_classestxt(self):
        """Create classes.txt file from the classes list."""
        with open(self.args.classes_txt_dir + 'classes.txt', 'w') as f:
            for class_name in self.classes_list:
                f.write(class_name+'\n')

def main(args):
    xmlfiles_pathlist = glob(args.xml_dir + "/*.xml")
    classes_list = []

    for xmlfile_path in xmlfiles_pathlist:
        process_xmlfile = GetDataFromXMLfile(xmlfile_path)
        xmlfile_datalists_list = process_xmlfile.get_datalists_list()
        CreateYOLOfile(xmlfile_datalists_list, classes_list, args)

    process_classesfile = CreateClasssesfile(classes_list, args)
    process_classesfile.create_classestxt()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert XML files to YOLO format.")
    parser.add_argument("--xml_dir", required=True, help="Path of directory with XML files.")
    parser.add_argument("--img_dir", required=True, help="Path of directory with image files.")
    parser.add_argument("--yolo_dir", required=True, help="Path where YOLO files will be created.")
    parser.add_argument("--classes_txt_dir", required=True, help="Path where classes.txt will be created.")
    parser.add_argument("--error_dir", required=True, help="Path where errors will be written to a text file.")
    
    args = parser.parse_args()
    
    main(args)
