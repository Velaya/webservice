# stable id provider

from flask import Flask, g, request, redirect, render_template, make_response
from config.config import instanznames, rdf_Service_Base_Uri
from db_connection import smns, smns_cache, smns_projects
from reverseproxy import ReverseProxied
from db_connection.common import dbStore

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

app.config["APPLICATION_ROOT"] = "/"

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_BINDS'] = {}

app.config['SQLALCHEMY_BINDS']['smns_collection'] = instanznames['smns_collection']
app.config['SQLALCHEMY_BINDS']['smns_projects'] = instanznames['smns_projects']
app.config['SQLALCHEMY_BINDS']['smns_cache'] = instanznames['smns_cache']


# important: first import all modules an then initialize the dbStore
for db_name, db in iter(dbStore.items()):
    db.app = app
    db.init_app(app)


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    serverlist = getattr(g, 'serverlist', dict())
    for c in serverlist.values():
        connectstring = '''mssql+pymssql://{userpass}@{server}'''.format(userpass=c.get('userpass'),
                                                                         server=c.get('server'))
        app.logger.debug("Closing connetion to %s" % connectstring)
        c.get('engine').dispose()
    serverlist.clear()


def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
           request.accept_mimetypes[best] > \
           request.accept_mimetypes['text/html']


def request_wants_rdf_xml():
    best = request.accept_mimetypes \
        .best_match(['application/rdf+xml', 'text/html'])
    return best == 'application/rdf+xml' and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']


def createBiocaseQueryAccNr(instance, database, accnr):
    instance = instance.lower()
    database = database.lower()
    print("accnr: %s" % accnr)
    if instance == 'smns' and database == 'collection':
        specimen = smns.getSpecimenFromAccessionNumber(accnr)
        print("SpecimenID: %s" % specimen)
        valid_projects = smns_cache.getProjectsforPackage()
        projectname = smns.getSpecimenProjectName(specimen, valid_projects)
        if projectname:
            url = "http://biocase.smns-bw.org/querytool/recordlist.cgi?dsa=" + projectname.rsplit('-', 1)[-1] + \
                  "&detail=unit&wrapper_url=http://biocase.smns-bw.org/pywrapper.cgi?dsa=" + projectname.rsplit('-', 1)[-1] + \
                  "&schema=http://www.tdwg.org/schemas/abcd/2.06&start=0&limit=12&groupby=---None---&filter=Unit_ID~" \
                  + accnr + "*"
            return url, projectname
    return None, None


def createBiocaseUrl3(instance, database, specimen):
    instance = instance.lower()
    database = database.lower()
    accnr = None
    projectname = None
    if instance == 'snsb' and database == 'collection':
        valid_projects = smns_cache.getProjectsforPackage()
        projectname = smns.getSpecimenProjectName(specimen, valid_projects)
        accnr_new = smns.getSpecimenAccessionNumber(specimen)
        if accnr_new:
            accnr = accnr_new.replace(" / ", "/")
            accnr = accnr.replace("/", " / ")
    if projectname and accnr:
        url = "http://biocase.smns-bw.org/querytool/recordlist.cgi?dsa=" + projectname.rsplit('-', 1)[-1] + \
              "&detail=unit&wrapper_url=http://biocase.smns-bw.org/pywrapper.cgi?dsa=" + projectname.rsplit('-', 1)[-1] + \
              "&schema=http://www.tdwg.org/schemas/abcd/2.06&start=0&limit=12&groupby=---None---&filter=Unit_ID~" \
              + accnr + "*"
        return url, projectname
    return None, None


def createBiocaseUrl4(instance, database, specimen, unit):
    instance = instance.lower()
    database = database.lower()
    projectname = None
    accnr = None
    if instance == 'smns' and database == 'collection':
        valid_projects = smns_cache.getProjectsforPackage()
        projectname = smns.getSpecimenProjectName(specimen, valid_projects)
        spacnr = smns.getSpecimenAccessionNumber(specimen)
        if spacnr:
            accnr_new = "%s/%s" % (spacnr, unit)
        else:
            accnr_new = "%s/%s" % (specimen, unit)
        if accnr_new:
            accnr = accnr_new.replace(" / ", "/")
            accnr = accnr.replace("/", " / ")
    if projectname and accnr:
        url = "http://biocase.smns-bw.org/querytool/details.cgi?dsa=" + projectname.rsplit('-', 1)[-1] + \
              "&detail=unit&wrapper_url=http://biocase.smns-bw.org/pywrapper.cgi?dsa=" + projectname.rsplit('-', 1)[-1] + \
              "&schema=http://www.tdwg.org/schemas/abcd/2.06&inst=SMNS&col=" + projectname + "&cat=" + accnr
        return url, projectname
    return None, None


def createBiocaseUrl5(instance, database, specimen, unit, part):
    instance = instance.lower()
    database = database.lower()
    accnr = None
    projectname = None
    if instance == 'smns' and database == 'collection':
        valid_projects = smns_cache.getProjectsforPackage()
        projectname = smns.getSpecimenProjectName(specimen, valid_projects)
        accnr_new = smns.getSpecimenIdentificationunitPartAccessionNumber(specimen, unit, part)
        if accnr_new:
            accnr = accnr_new.replace(" / ", "/")
            accnr = accnr.replace("/", " / ")
    if projectname and accnr:
        url = "http://biocase.smns-bw.org/querytool/details.cgi?dsa=" + projectname.rsplit('-', 1)[-1] + \
              "&detail=unit&wrapper_url=http://biocase.smns-bw.org/pywrapper.cgi?dsa=" + projectname.rsplit('-', 1)[-1] + \
              "&schema=http://www.tdwg.org/schemas/abcd/2.06&inst=SMNS&col=" + projectname + "&cat=" + accnr
        return url, projectname
    return None, None


@app.route('/<string:instance>/<string:database>/<int:specimen>')
def specimen_incomplete(instance, database, specimen):
    database = database.lower()
    if database == 'projects':
        if request_wants_rdf_xml():
            rdfUrl = '/'.join((rdf_Service_Base_Uri, instance, database, str(specimen)))
            print(rdfUrl)

            rp = redirect(rdfUrl, 303)
        else:
            projecturl = smns_projects.getProjectUrl(specimen)
            if projecturl:
                rp = redirect(projecturl, 303)
            else:
                rp = make_response(render_template('not_found.html'), 404)
    else:
        biocaseurl, projectName = createBiocaseUrl3(instance, database, specimen)
        if biocaseurl:
            if request_wants_rdf_xml():
                rdfUrl = '/'.join((rdf_Service_Base_Uri, instance, database, projectName, str(specimen)))
                print(rdfUrl)
                rp = redirect(rdfUrl, 303)
            else:
                rp = redirect(biocaseurl, 303)
        else:
            rp = make_response(render_template('not_found.html'), 404)
    rp.headers['Vary'] = 'Accept'
    return rp


# @cache.cached(timeout=50)
@app.route('/<string:instance>/<string:database>/<int:specimen>/<int:unit>')
def specimen_unit(instance, database, specimen, unit):
    biocaseurl, projectName = createBiocaseUrl4(instance, database, specimen, unit)
    if biocaseurl:
        if request_wants_rdf_xml():
            rdfUrl = '/'.join((rdf_Service_Base_Uri, instance, database, projectName, str(specimen), str(unit)))
            print(rdfUrl)
            rp = redirect(rdfUrl, 303)
        else:
            rp = redirect(biocaseurl, 303)
    else:
        rp = make_response(render_template('not_found.html'), 404)
    rp.headers['Vary'] = 'Accept'
    return rp


@app.route('/<string:instance>/<string:database>/<int:specimen>/<int:unit>/<int:part>')
def specimen_unit_part(instance, database, specimen, unit, part):
    biocaseurl, projectName = createBiocaseUrl5(instance, database, specimen, unit, part)
    if biocaseurl:
        if request_wants_rdf_xml():
            rdfUrl = '/'.join(
                (rdf_Service_Base_Uri, instance, database, projectName, str(specimen), str(unit), str(part)))
            print(rdfUrl)

            rp = redirect(rdfUrl, 303)
        else:
            rp = redirect(biocaseurl, 303)
    else:
        rp = make_response(render_template('not_found.html'), 404)
    rp.headers['Vary'] = 'Accept'
    return rp


@app.route('/Collection/<specimen_unit_part_>')
def specimen_unit_part_Collection(specimen_unit_part_):
    instance = 'SMNS'
    database = 'Collection'
    biocaseurl = None
    rdfurl = ""
    v = specimen_unit_part_.split('-')
    if len(v) == 3:
        specimen, unit, part = v
        biocaseurl, projectName = createBiocaseUrl5(instance, database, specimen, unit, part)
        rdfurl = '/'.join((rdf_Service_Base_Uri, instance, database, projectName, str(specimen), str(unit), str(part)))
    if len(v) == 2:
        specimen, unit = v
        print("Specimen: %s, Unit: %s" % (specimen, unit))
        biocaseurl, projectName = createBiocaseUrl4(instance, database, specimen, unit)
        rdfurl = '/'.join((rdf_Service_Base_Uri, instance, database, projectName, str(specimen), str(unit)))
    if len(v) == 1:
        specimen = v
        biocaseurl, projectName = createBiocaseUrl3(instance, database, specimen)
        rdfurl = '/'.join((rdf_Service_Base_Uri, instance, database, projectName, str(specimen)))
        print("Specimen: %s, url: %s" % (specimen, biocaseurl))

    if biocaseurl:
        if request_wants_rdf_xml():
            print(rdfurl)
            rp = redirect(rdfurl, 303)
        else:
            rp = redirect(biocaseurl, 303)
    else:
        rp = make_response(render_template('not_found.html'), 404)
    rp.headers['Vary'] = 'Accept'
    return rp


@app.route('/object/<string:accessionnumber>')
def viaAccessionNumber(accessionnumber):
    if request_wants_rdf_xml():
        rp = make_response('', 406)
    else:
        instance = 'SMNS'
        database = 'Collection'
        biocaseurl, projectname = createBiocaseQueryAccNr(instance, database, accessionnumber)
        if biocaseurl:
            rp = redirect(biocaseurl, 303)
        else:
            rp = make_response(render_template('not_found.html'), 404)
    rp.headers['Vary'] = 'Accept'
    return rp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
