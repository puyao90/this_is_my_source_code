import json
import xml.etree.ElementTree as ET

def json_to_xsd(json_data, root_element_name):
    # Create the root element of the XSD
    root = ET.Element("xs:schema", xmlns_xs="http://www.w3.org/2001/XMLSchema")
    
    # Create the main complex type
    main_complex_type = ET.SubElement(root, "xs:element", name=root_element_name)
    complex_type = ET.SubElement(main_complex_type, "xs:complexType")
    sequence = ET.SubElement(complex_type, "xs:sequence")

    # Function to recursively create elements from JSON
    def create_elements(data, parent):
        for key, value in data.items():
            if isinstance(value, dict):
                # If the value is a dictionary, create a complex type
                element = ET.SubElement(parent, "xs:element", name=key)
                sub_complex_type = ET.SubElement(element, "xs:complexType")
                sub_sequence = ET.SubElement(sub_complex_type, "xs:sequence")
                create_elements(value, sub_sequence)
            elif isinstance(value, list):
                # If the value is a list, create an element with minOccurs and maxOccurs
                element = ET.SubElement(parent, "xs:element", name=key)
                item_complex_type = ET.SubElement(element, "xs:complexType")
                item_sequence = ET.SubElement(item_complex_type, "xs:sequence")
                # Assuming all items in the list are of the same type
                create_elements(value[0], item_sequence)  # Use the first item to determine structure
                element.set("minOccurs", "0")
                element.set("maxOccurs", "unbounded")
            else:
                # Otherwise, it's a simple type
                element = ET.SubElement(parent, "xs:element", name=key)
                if isinstance(value, str):
                    element.set("type", "xs:string")
                elif isinstance(value, int):
                    element.set("type", "xs:int")
                elif isinstance(value, float):
                    element.set("type", "xs:float")
                elif isinstance(value, bool):
                    element.set("type", "xs:boolean")
    
    # Start creating elements from the JSON data
    create_elements(json_data, sequence)

    return ET.tostring(root, encoding='utf-8', xml_declaration=True).decode('utf-8')

# Load JSON data from a file
with open('/Users/sphy/workspace/CM3070/sample/sample.json', 'r') as f:
    json_data = json.load(f)

# Generate XSD schema
xsd_schema = json_to_xsd(json_data, root_element_name="Programs")

# Save the XSD schema to a file
with open('schema.xsd', 'w') as f:
    f.write(xsd_schema)

print("XSD schema generated successfully!")
