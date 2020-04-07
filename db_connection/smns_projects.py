# snsb_projects

from flask_sqlalchemy import SQLAlchemy
from db_connection.common import dbStore

db = SQLAlchemy()

dbStore['smns_projects'] = db


class Project(db.Model):
   __bind_key__ = 'smns_projects'
   __tablename__ = 'Project'
   ProjectID = db.Column(db.Integer, primary_key=True)
   ProjectURL = db.Column(db.Text)
 

def getProjectUrl(projectid):
    project = Project.query.filter_by(ProjectID = projectid).first()
    if project:
        return project.ProjectURL
    return none
