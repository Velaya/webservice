# smns

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from db_connection.common import dbStore

db = SQLAlchemy()

dbStore['smns_collection'] = db


class CollectionSpecimen(db.Model):
    __bind_key__ = 'smns_collection'
    __tablename__ = 'CollectionSpecimen'
    CollectionSpecimenID = db.Column(db.Integer, primary_key=True)
    AccessionNumber = db.Column(db.Text)


class CollectionProject(db.Model):
    __bind_key__ = 'smns_collection'
    __tablename__ = 'CollectionProject'
    CollectionSpecimenID = db.Column(db.Integer, primary_key=True)
    ProjectID = db.Column(db.Integer, primary_key=True)


class IdentificationUnit(db.Model):
    __bind_key__ = 'smns_collection'
    __tablename__ = 'IdentificationUnit'
    CollectionSpecimenID = db.Column(db.Integer, primary_key=True)
    IdentificationUnitID = db.Column(db.Integer, primary_key=True)


class CollectionSpecimenPart(db.Model):
    __bind_key__ = 'smns_collection'
    __tablename__ = 'CollectionSpecimenPart'
    CollectionSpecimenID = db.Column(db.Integer, primary_key=True)
    SpecimenPartID = db.Column(db.Integer, primary_key=True)
    AccessionNumber = db.Column(db.Text)


class IdentificationUnitInPart(db.Model):
    __bind_key__ = 'smns_collection'
    __tablename__ = 'IdentificationUnitInPart'
    CollectionSpecimenID = db.Column(db.Integer, primary_key=True)
    IdentificationUnitID = db.Column(db.Integer, primary_key=True)
    SpecimenPartID = db.Column(db.Integer, primary_key=True)


class ProjectProxy(db.Model):
    __bind_key__ = 'smns_collection'
    __tablename__ = 'ProjectProxy'
    ProjectID = db.Column(db.Integer, primary_key=True)
    Project = db.Column(db.Text)


def getSpecimenAccessionNumber(specimenid):
    accIDs = CollectionSpecimen.query.filter_by(CollectionSpecimenID=specimenid).first()
    if accIDs:
        return accIDs.AccessionNumber
    else:
        return None


def getSpecimenIdentificationAccessionNumber(specimenid, unitid):
    idUnits = IdentificationUnit.query.filter_by(CollectionSpecimenID=specimenid, IdentificationUnitID=unitid).first()
    if idUnits:
        accessionNumber = getSpecimenAccessionNumber(specimenid)
        if not accessionNumber:
            accesionNumber = specimenid
        accNrUnitId = "%s / %s" % (accessionNumber, unitid)
        return accNrUnitId
    return None


def getSpecimenPartAccessionNumber(specimenid, partid):
    accIDs = CollectionSpecimenPart.query.filter_by(CollectionSpecimenID=specimenid, SpecimenPartID=partid).first()
    if accIDs:
        return accIDs.AccessionNumber
    return None


def getSpecimenIdentificationunitPartAccessionNumber(specimenid, unitid, partid):
    accID = getSpecimenAccessionNumber(specimenid)
    part = partid
    print(accID)
    if not accID:
        accID = specimenid
    part = getSpecimenPartAccessionNumber(specimenid, partid)
    print("Part %s" % part)
    if not part:
        part = partid
    accnr = "%s / %s / %s" % (accID, unitid, part)
    return accnr


def getSpecimenProjectName(specimenid, valid_projectnumbers=None):
    if valid_projectnumbers:
        projectnumbers = CollectionProject.query.filter(and_(CollectionProject.CollectionSpecimenID == specimenid,
                                                             CollectionProject.ProjectID.in_(valid_projectnumbers)))
    else:
        projectnumbers = CollectionProject.query.filter_by(CollectionSpecimenID=specimenid)
    if projectnumbers:
        projectnumber = projectnumbers.first()  # We do not know which ABCD packages is really shown in biocase!
        if projectnumber:
            print()
            projectname = ProjectProxy.query.filter_by(ProjectID=projectnumber.ProjectID).first().Project
        else:
            projectname = None
    else:
        projectname = None
    return projectname


def getSpecimenFromAccessionNumber(accnr):
    specimenids = CollectionSpecimen.query.filter_by(AccessionNumber=accnr).first()
    if specimenids:
        specimenid = specimenids.CollectionSpecimenID
        return specimenid
    return None
