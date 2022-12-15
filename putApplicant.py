"""

attr_id,class
cooling@residential_listing_-_feature_details@house_listing@homeseekers.csv,cooling
cooling@house_listing@nky.csv,cooling
ac@house_listing@windermere.csv,cooling
house_location@house_listing@nky.csv,address
location@residential_listing_-_basic_features@house_listing@homeseekers.csv,address
address@house_listing@windermere.csv,address
house_location@house_listing@yahoo.csv,address
house_location@house_listing@texas.csv,address

company@file.csv,Organization.name
ceo@file.csv,Person.name
file.csv,Organization-ceo-Person
file.csv,Organization-location-City
file.csv,Person-livesIn-City


business_info_ssd = (sn
                     .SSD(business_info, ontology, name='business-info')
                     .map(Column("company"), DataNode(ClassNode("Organization"), "name"))
                     .map(Column("ceo"), DataNode(ClassNode("Person"), "name"))
                     .map(Column("city"), DataNode(ClassNode("City"), "name"))
                     .map(Column("state"), DataNode(ClassNode("State"), "name"))
                     .link("Organization", "operatesIn", "City")
                     .link("Organization", "ceo", "Person")
                     .link("City", "state", "State"))

business_info_ssd.show()

print()
print("Displaying businessInfo.csv Semantic Source Description (SSD)")
input("press any key to continue...")

#
# We also have just a string shorthand...
#

ontology_file = 'tests/resources/owl/dataintegration_report_ontology.ttl'

datasets = [
    'tests/resources/data/businessInfo.csv',
    'tests/resources/data/EmployeeAddresses.csv',
    'tests/resources/data/getCities.csv',
    'tests/resources/data/getEmployees.csv',
    'tests/resources/data/postalCodeLookup.csv',
]

map_file = tests/resources/data/example-map-file.csv

> cat example-map-file.csv

attr_id, class
name@EmployeeAdddress.csv, Person.name
address@EmployeeAdddress.csv, Place.name
postcode@EmployeeAdddress.csv, Place.postalCode
getCities.csv@city, City.name
getCities.csv@state, State.name
employer@getEmployees.csv, Organization.name
employee@getEmployees.csv, Person.name
zipcode@postalCodeLookup.csv, Place.postalCode
city@postalCodeLookup.csv, City.name
state@postalCodeLookup.csv, State.name

link_file = tests/resources/data/example-link-file.csv

> cat example-link-file.csv

file, src, type, dst
EmployeeAdddress.csv, Person, livesIn, Place
getCities.csv, City, state, State
getEmployees.csv, Person, worksFor, Organization
postalCodeLookup.csv, City, state, State
postalCodeLookup.csv, City, isPartOf, Place


 input
  Some knowledge about the ontology or where you want to end up...
  /some/junk/test1.csv  - contains columns: name, birth, city, state, workplace
  /some/junk/test2.csv  - contains columns: state, city
  /some/junk/test3.csv  - contains columns: company, ceo, city, state
  /some/junk/test4.csv  - contains columns: employer, employee
  /some/junk/test5.csv  - contains columns: zipcode, city, state
  ..
  ..
  ..
  ...
 output
  SSD: semantic source description files
    /some/junk/test1.ssd
    /some/junk/test2.ssd
    /some/junk/test3.ssd
    /some/junk/test4.ssd
    /some/junk/test5.ssd
    ...
    ...
    ...
"""

# ===========
#    SETUP
# ===========
try:
    import serene
except ImportError as e:
    import sys
    sys.path.insert(0, '../')
    import serene

import datetime
import pandas as pd
import os

from serene import SSD, Status, DataProperty, Mapping, ObjectProperty, Column, Class, DataNode, ClassNode

# We have these datasets:
#
# businessInfo.csv company,ceo,city,state
# EmployeeAddresses.csv: FirstName,LastName,address,postcode
# getCities: state,city
# getEmployees: employer,employee
# postalCodeLookup: zipcode,city,state
#
# and we want to predict these...
#
# personalInfo: name,birthDate,city,state,workplace
#


# =======================
#
#  Step 1: Start with a connection to the server...
#
# =======================
sn = serene.Serene(
    host='127.0.0.1',
    port=8080,
)
print(sn)
#
# >>> Serene(127.0.0.1:9000)
#

# =======================
#
#  Step 2: Upload some training datasets...
#
# =======================
#
# assigning the DataSet to a variable will help us keep track...
#
print()
print("First we upload some datasets...")
data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests", "resources", "data")
owl_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests", "resources", "owl")

business_info = sn.datasets.upload(os.path.join(data_path, 'businessInfo2.csv'))
employee_address = sn.datasets.upload(os.path.join(data_path, 'EmployeeAddresses2.csv'))
get_cities = sn.datasets.upload(os.path.join(data_path, 'getCities.csv'))
# get_employees = sn.datasets.upload(os.path.join(data_path, 'getEmployees.csv'))
postal_code = sn.datasets.upload(os.path.join(data_path, 'postalCodeLookup.csv'))
gms_employees = sn.datasets.upload(os.path.join(data_path, 'GMSEmployees.csv'))
mock_employees = sn.datasets.upload(os.path.join(data_path, 'MOCK_EMPLOYEES.csv'))
# ps_location = sn.datasets.upload(os.path.join(data_path, 'PS_LOCATION_TBL-1000.csv'))
ps_personal_data_updated = sn.datasets.upload(os.path.join(data_path, 'PS_PERSONAL_DATA_UPDATED.csv'))

datasets = [
    business_info,
    employee_address,
    get_cities,
    # get_employees,
    postal_code,
    gms_employees,
    # ps_location
    ps_personal_data_updated,
    mock_employees
]

print("Done.")
#
# lets have a look...
#
for d in datasets:
    print("DataSet:", d.id)
    print("        ", d.description)
    print("        ", d.columns)
    print()

# =======================
#
#  Step 3: Upload some ontologies
#
# =======================

print()
print("Now we handle the ontologies...")
#
# first let's see the ontologies that exist
#
ontologies = sn.ontologies.items

if len(ontologies):
    print()
    print("Displaying first ontology on the server...")
    ontologies[0].show()

    # input("Press enter to continue")

# #
# # The most straightforward way is to upload an OWL file directly...
# #
# ontology = sn.ontologies.upload('tests/resources/owl/dataintegration_report_ontology.ttl')
#
# print("Showing the uploaded ontology...")
#
# ontology.show()
#
# input("Press enter to continue...")
#
# #
# # Or if you want to check it first you can do...
# #
# local_ontology = serene.Ontology('tests/resources/owl/dataintegration_report_ontology.ttl')
ontology_local = serene.Ontology(os.path.join(owl_path, 'pbApplicant.ttl'))
# ontology_local = serene.Ontology(os.path.join(owl_path, 'paper.ttl'))

# Have a quick look...
#
ontology_local.show()
# input("press any key to continue...")
#
# or output to an owl file if you want...
ontology_local.to_turtle(os.path.join(owl_path, 'test.ttl'))


#
print()
print("Displaying local ontology...")
# input("Press enter to continue...")

#
# If ok, we can upload this to the server as well...
#
ontology = sn.ontologies.upload(ontology_local)


# ===============
#
#  Step 4: Now start labelling some datasets with SSDs
#
# ===============

# First lets have a look at the datasets...
for d in datasets:
    print("DataSet:", d.id)
    print("         ", d.description)
    print(d.sample)
    print()

# And at the datanodes we'll need to map
print("DataNodes:")
print(ontology.data_nodes)


# businessInfo.csv company,ceo,city,state
# EmployeeAddresses.csv: name,address,postcode
# getCities: state,city
# getEmployees: employer,employee
# postalCodeLookup: zipcode,city,state
# gms_employees: Employee ID,First Name,Last Name,Email - Primary Work,Primary Address - Postal Code,Primary Address - Line 1,Primary Address - Line 2,Primary Home Address - State
# ps_location_tbl-1000: LOCATION,EFFDT,EFF_STATUS,DESCR,DESCR_AC,DESCRSHORT,COUNTRY,ADDRESS1,CITY,STATE,POSTAL,COUNTRY_CODE,PHONE,LANG_CD,LASTUPDDTTM,COMMENTS_2000

# Mocked data EMPLID, LAST_NAME, FIRST_NAME, EMAIL, ADDRESS1, CITY, STATE, POSTAL
# mock_employees_ssd = (sn
#                       .SSD(mock_employees, ontology, name='mock-employees')
#                       .map(Column("LAST_NAME"), DataNode(ClassNode("Name"), "Last_Name"))
#                       .map(Column("POSTAL"), DataNode(ClassNode("Address"), "Zip"))
#                       .map(Column("ADDRESS1"), DataNode(ClassNode("Address"), "Street"))
#                       .map(Column("CITY"), DataNode(ClassNode("Address"), "City"))
#                       .map(Column("STATE"), DataNode(ClassNode("Address"), "State"))
#                       .map(Column("FIRST_NAME"), DataNode(ClassNode("Name"), "First_Name"))
#                       .map(Column("EMAIL"), DataNode(ClassNode("Contact"), "Email"))
#                       .link("Person", "has", "Address")
#                       .link("Person", "has", "Name")
#                       .link("Person", "has", "Contact"))

# mock_employees_ssd.show()
# # input("press any key to continue...")
# print(mock_employees_ssd.json)
# f = open("mock_employees_ssd.json", "a")
# f.write(mock_employees_ssd.json)
# f.close()

gms_employees_ssd = (sn
                     .SSD(gms_employees, ontology, name='gms-employees')
                     .map(Column("Email - Primary Work"), DataNode(ClassNode("Contact"), "Email"))
                     .map(Column("Last Name"), DataNode(ClassNode("Name"), "Last_Name"))
                     .map(Column("Primary Address - Postal Code"), DataNode(ClassNode("Address"), "Zip"))
                     .map(Column("Primary Address - Line 1"), DataNode(ClassNode("Address"), "Street"))
                     .map(Column("Primary Address - Line 2"), DataNode(ClassNode("Address"), "City"))
                     .map(Column("Primary Home Address - State"), DataNode(ClassNode("Address"), "State"))
                     .map(Column("First Name"), DataNode(ClassNode("Name"), "First_Name"))
                     .link("Person", "has", "Address")
                     .link("Person", "has", "Name")
                     .link("Person", "has", "Contact"))

gms_employees_ssd.show()
print(gms_employees_ssd.json)
f = open("gms_employees_ssd.json", "a")
f.write(gms_employees_ssd.json)
f.close()

# ps_personal_data_updated: EMPLID,LAST_NAME,FIRST_NAME,EMAIL,BIRTHDATE,ETHNIC_GROUP,SEX
ps_personal_data_updated_ssd = (sn
                     .SSD(ps_personal_data_updated, ontology, name='ps_personal_data_updated')
                     .map(Column("EMAIL"), DataNode(ClassNode("Contact"), "Email"))
                     .map(Column("LAST_NAME"), DataNode(ClassNode("Name"), "Last_Name"))
                     .map(Column("FIRST_NAME"), DataNode(ClassNode("Name"), "First_Name"))
                     .link("Person", "has", "Name")
                     .link("Person", "has", "Contact"))

ps_personal_data_updated_ssd.show()
print(ps_personal_data_updated_ssd.json)
f = open("ps_personal_data_updated_ssd.json", "a")
f.write(ps_personal_data_updated_ssd.json)
f.close()

# RowNum,SETID,LOCATION,EFFDT,EFF_STATUS,DESCR,DESCR_AC,DESCRSHORT,COUNTRY,ADDRESS1,CITY,STATE,POSTAL,COUNTRY_CODE,PHONE,LANG_CD,LASTUPDDTTM,COMMENTS_2000
# ps_location_ssd = (sn
#                    .SSD(ps_location, ontology, name='gms-employees')
#                    .map(Column("Primary Address - Postal Code"), DataNode(ClassNode("Address"), "Zip"))
#                    .map(Column("ADDRESS1"), DataNode(ClassNode("Address"), "Street"))
#                    .map(Column("CITY"), DataNode(ClassNode("Address"), "City"))
#                    .map(Column("STATE"), DataNode(ClassNode("Address"), "State"))
#                    .link("Person", "has", "Address"))

# company,ceo,last,city,state
# business_info_ssd = (sn
#                      .SSD(business_info, ontology, name='business-info')
#                      .map(Column("ceo"), DataNode(ClassNode("Name"), "First_Name"))
#                      .map(Column("last"), DataNode(ClassNode("Name"), "Last_Name"))
#                      .map(Column("city"), DataNode(ClassNode("Address"), "City"))
#                      .map(Column("state"), DataNode(ClassNode("Address"), "State"))
#                      .link("Person", "has", "Address")
#                      .link("Person", "has", "Name"))
# business_info_ssd.show()
# print(business_info_ssd.json)
# f = open("business_info_ssd.json", "a")
# f.write(business_info_ssd.json)
# f.close()

print()
print("Displaying businessInfo.csv Semantic Source Description (SSD)")
# input("press any key to continue...")

#
# We also have just a string shorthand...
#
employee_address_ssd = (sn
                        .SSD(employee_address, ontology, name='employee-addr')
                        .map("FirstName", DataNode(ClassNode("Name"), "First_Name"))
                        .map("LastName", DataNode(ClassNode("Name"), "Last_Name"))
                        .map("postcode", DataNode(ClassNode("Address"), "Zip"))
                        .link("Person", "has", "Address")
                        .link("Person", "has", "Name"))

employee_address_ssd.show()

print()
print("Displaying EmployeeAdddress.csv Semantic Source Description (SSD)")
# input("press any key to continue...")

get_cities_ssd = (sn
                  .SSD(get_cities, ontology, name='cities')
                  .map(Column("city"), DataNode(ClassNode("Address"), "City"))
                  .map(Column("state"), DataNode(ClassNode("Address"), "State"))
                  .link("Person", "has", "Address"))

get_cities_ssd.show()

print()
print("Displaying getCities.csv Semantic Source Description (SSD)")
# input("press any key to continue...")

# get_employees_ssd = (sn
#                      .SSD(get_employees, ontology, name='employees')
#                      .map("FirstName", "Person.Name.First_Name")
#                      .map("LastName", "Person.Name.Last_Name")
#                      .link("Person", "has", "Name"))
#
# get_employees_ssd.show()

print()
print("Displaying getEmployees.csv Semantic Source Description (SSD)")
# input("press any key to continue...")

postal_code_ssd = (sn
                   .SSD(postal_code, ontology, name='postal-code')
                   .map(Column("zipcode"), DataNode(ClassNode("Address"), "Zip"))
                   .map(Column("city"), DataNode(ClassNode("Address"), "City"))
                   .map(Column("state"), DataNode(ClassNode("Address"), "State"))
                   .link("Person", "has", "Address")
                   )

# postal_code_ssd.show()

print()
print("Displaying postalCodeLookup.csv Semantic Source Description (SSD)")
# input("press any key to continue...")

# postal_code_ssd2 = (sn
#                     .SSD(postal_code, ontology, name='postal-code')
#                     .map(Column("zipcode"), "Place.postalCode")
#                     .map(Column("city"), "City.name")
#                     .map(Column("state"), "State.name")
#                     .link("City", "state", "State")
#                     .link("City", "isPartOf", "Place")
#                     )
#
# postal_code_ssd2.show()

# upload all these to the server. Here we ignore the return value (the SSD object will be updated)

for ssd in [
    # business_info_ssd,
    gms_employees_ssd,
    employee_address_ssd,
    # mock_employees_ssd,
    ps_personal_data_updated_ssd,
    get_cities_ssd,
    # get_employees_ssd,
    postal_code_ssd]:
    sn.ssds.upload(ssd)

# ==========
#
#  Step 5. Create an Octopus data integration object...
#
# ==========

octo_local = sn.Octopus(
    ssds=[
        # business_info_ssd,
        employee_address_ssd,
        get_cities_ssd,
        gms_employees_ssd,
        # get_employees_ssd,
        postal_code_ssd
    ],
    ontologies=[ontology],
    name='octopus-test',
    description='Testing example for places and companies',
    resampling_strategy="NoResampling",  # optional
    num_bags=100,  # optional
    bag_size=10,  # optional
    model_type="randomForest",
    modeling_props={
        "compatibleProperties": True,
        "ontologyAlignment": False,
        "addOntologyPaths": False,
        "mappingBranchingFactor": 50,
        "numCandidateMappings": 10,
        "topkSteinerTrees": 50,
        "multipleSameProperty": False,
        "confidenceWeight": 1.0,
        "coherenceWeight": 1.0,
        "sizeWeight": 0.5,
        "numSemanticTypes": 10,
        "thingNode": False,
        "nodeClosure": True,
        "propertiesDirect": True,
        "propertiesIndirect": True,
        "propertiesSubclass": True,
        "propertiesWithOnlyDomain": True,
        "propertiesWithOnlyRange": True,
        "propertiesWithoutDomainRange": False,
        "unknownThreshold": 0.05
    },
    feature_config={
        "activeFeatures": [
            "num-unique-vals",
            "prop-unique-vals",
            "prop-missing-vals",
            "ratio-alpha-chars",
            "prop-numerical-chars",
            "prop-whitespace-chars",
            "prop-entries-with-at-sign",
            "prop-entries-with-hyphen",
            "prop-range-format",
            "is-discrete",
            "entropy-for-discrete-values",
            "shannon-entropy"
        ],
        "activeFeatureGroups": [
            "inferred-data-type",
            "char-dist-features",
            "stats-of-text-length",
            "stats-of-numeric-type",
            "prop-instances-per-class-in-knearestneighbours",
            "mean-character-cosine-similarity-from-class-examples",
            "min-editdistance-from-class-examples",
            "min-wordnet-jcn-distance-from-class-examples",
            "min-wordnet-lin-distance-from-class-examples"
        ],
        "featureExtractorParams": [
            {
                "name": "prop-instances-per-class-in-knearestneighbours",
                "num-neighbours": 3
            }, {
                "name": "min-editdistance-from-class-examples",
                "max-comparisons-per-class": 3
            }, {
                "name": "min-wordnet-jcn-distance-from-class-examples",
                "max-comparisons-per-class": 3
            }, {
                "name": "min-wordnet-lin-distance-from-class-examples",
                "max-comparisons-per-class": 3
            }
        ]
    }
)

# add this to the endpoint...
print("Now we upload to the server")
octo = sn.octopii.upload(octo_local)

# =======================
#
# Step 6. Train
#
# =======================

print()
print("Next we can train the Octopus")
print("The initial state for {} is {}".format(octo.id, octo.state))
print("Training...")
octo.train()
print("Done.")
print("The final state for {} is {}".format(octo.id, octo.state))

if octo.state.status in {Status.ERROR}:
    print("Something went wrong. Failed to train the Octopus.")
    # exit()

# =======================
#
#  Step 7. Run predictions
#
# =======================

personal_info = sn.datasets.upload(os.path.join(data_path, 'MOCK_EMPLOYEES.csv'))
predicted = octo.predict(personal_info)

print()
print("Predicted schema matcher results::")
print()
schema_results = octo.matcher_predict(personal_info, features=True)
print(schema_results)
schema_results.to_csv("employees_features.csv", index=False)
# input("Press any key to continue...")

print()
print("Predicted results::")
print()
for pred in predicted:
    print(pred.score)
    # pred.ssd.show()
    # input("Press enter to continue...")

# =======================
#
#  Step 7. Correct the predicted result...
#
# =======================

print("the best is number 0!")

predicted_ssd = predicted[0].ssd
predicted_ssd.show()
# mock_employees_ssd.show()

print("Showing first guess...")
# input("Press any key to continue...")

# print("Fixing DOB column")
# predicted_ssd.remove(Column("DOB"))
#
# print("Removing DOB assignment")
# # input("Press any key to continue...")
#
# predicted_ssd.map(Column("DOB"), DataNode(ClassNode("Person"), "birthDate"))
# predicted_ssd.link("Person", "worksFor", "Organization")
# # predicted_ssd.show(outfile="personInfo.dot")
# predicted_ssd.show()

print(predicted_ssd.json)
f = open("predicted_ssd.json", "a")
f.write(predicted_ssd.json)
f.close()
