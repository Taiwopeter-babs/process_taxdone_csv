FILE_NAME = "migration_data.xlsx"
USERS_SHEET_NAME = "Users Details"
DECLARATIONS_SHEET_NAME = "Declarations"
USER_COLUMNS = {
    "Admin?": "accountType",
    "birth date - User": "dob",
    "manualId": "filingId",
    "FirstName": "firstName",
    "LastName": "lastName",
    "email": "email",
    "Phone": "phone",
}

DECLARATION_COLUMNS = [
    "unique_id", "year",
]

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
# DATETIME_FORMAT = "%Y-%m-%d"

DECLARATION_MAPPER = {
    "activity - User": "All Activities",
    "Kids": "Children",
    "familySocialHelpReceived": "FamilySocial Help",
    "self-employment - User": "Self Employment",
    "jobsUser": "Employment Job",
    "Accounts&Securities": "Securities",
    "otherActivityIncome - User": "Other Activity Income",
    "otherActivityExpenses - User": "Other Activity Expenses",
    "transportUser": "Transports",
    "Education - User": "Education Expenses",
    "pensionPillarContributions - User": "Pension Pillar Ctrbn",
    "debts": "Debt",
    "LifePensionInsurances": "Life Insurance",
    "realEstate": "Real Estate",
    "managementFees": "Management Fees",
    "inheritance - User": "Inheritances",
    "donations": "Donation",
    "tangibleAssets": "Tangible Assets",
    "politicalContributions": "Political Ctrbn",
    "healthInsurance": "Health Insurance",
    "healthExpenses": "Health Expenses"
}

# SHEETS_TO_PARSE = ['All Activities', 'Children', 'FamilySocial Help', 'Self Employment',
#                    'Invoices', 'Employment Job', 'Other Activity Income', 'Other Activity Expenses',
#                    'Transports', 'Education Expenses', 'Securities', 'Pension Pillar Ctrbn ', 'Debt',
#                    'Life Insurance', 'Real Estate', 'Management Fees', 'Inheritances', 'Donation', 'Tangible Assets',
#                    'Political Ctrbn', 'Health Insurance', 'Health Expenses'
#                    ]

SHEETS_TO_PARSE = [value for value in DECLARATION_MAPPER.values()]
