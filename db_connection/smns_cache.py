# snsb_projects

from flask_sqlalchemy import SQLAlchemy
from db_connection.common import dbStore

db = SQLAlchemy()

dbStore['smns_cache'] = db


class ProjectTargetPackage(db.Model):
   __bind_key__ = 'smns_cache'
   __tablename__ = 'ProjectTargetPackage'
   ProjectID = db.Column(db.Integer, primary_key=True)
   TargetID = db.Column(db.Integer, primary_key=True)
   Package = db.Column(db.Integer, primary_key=True)
 

def getProjectsforPackage(packagename="ABCD"):
    projects = []
    for row in ProjectTargetPackage.query.filter_by(Package = packagename).all():
        projects.append(row.ProjectID)
    return projects
