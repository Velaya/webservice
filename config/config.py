rdf_Service_Base_Uri = 'http://services.snsb.info/dwbc/v1'

instanznames = {}

_password = '******'

# smns

DATABASENAME = "DiversityProjects_SMNS"
_database = '''mssql+pymssql://dbo_smns:''' + _password + '''@smns.diversityworkbench.de:5432/''' + DATABASENAME

instanznames['smns_projects'] = _database

DATABASENAME = "DiversityCollection_SMNS"
_database = '''mssql+pymssql://dbo_smns:''' + _password + '''@smns.diversityworkbench.de:5432/''' + DATABASENAME

instanznames['smns_collection'] = _database

DATABASENAME = "DiversityCollectionCache01_SMNS"
_database = '''mssql+pymssql://dbo_smns:''' + _password + '''@smns.diversityworkbench.de:5432/''' + DATABASENAME

instanznames['smns_cache'] = _database
