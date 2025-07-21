import os
from app import create_app, db
from app.models.user import User
from app.models.property import Property
from app.models.lease import Lease
from app.models.document import Document
from app.models.message import Message
from app.models.maintenance_request import MaintenanceRequest

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Property': Property,
        'Lease': Lease,
        'Document': Document,
        'Message': Message,
        'MaintenanceRequest': MaintenanceRequest
    }

if __name__ == '__main__':
    app.run(debug=True)