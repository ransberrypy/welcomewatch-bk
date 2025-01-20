# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)


CORS(app, resources={
    r"/api/*": {  # All routes under /api/
        "origins": ["https://welcomewatch.netlify.app/"],  # Your React app's URL
        "methods": ["GET", "POST", "PUT", "DELETE"],  # Allowed methods
        "allow_headers": ["Content-Type"]  # Allowed headers
    }
})


instance_path = os.environ.get('INSTANCE_PATH', '/app/instance')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{instance_path}/visitors.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visitors.db'


db = SQLAlchemy(app)

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visitorName = db.Column(db.String(100), nullable=False)
    purpose = db.Column(db.String(200), nullable=False)
    hostName = db.Column(db.String(100), nullable=False)
    phoneNumber = db.Column(db.String(20), nullable=False)
    timeIn = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Waiting')

@app.route('/api/visitors', methods=['GET'])
def get_visitors():
    visitors = Visitor.query.all()
    return jsonify([{
        'id': v.id,
        'visitorName': v.visitorName,
        'purpose': v.purpose,
        'hostName': v.hostName,
        'phoneNumber': v.phoneNumber,
        'timeIn': v.timeIn.strftime('%Y-%m-%d %H:%M:%S'),
        'status': v.status
    } for v in visitors])

@app.route('/api/visitors', methods=['POST'])
def create_visitor():
    data = request.json
    visitor = Visitor(
        visitorName=data['visitorName'],
        purpose=data['purpose'],
        hostName=data['hostName'],
        phoneNumber=data['phoneNumber'],
        timeIn=datetime.utcnow()
    )
    db.session.add(visitor)
    db.session.commit()
    return jsonify({'message': 'Visitor registered successfully'}), 201


@app.route('/api/visitors/<int:id>/usher', methods=['PUT'])
def usher_visitor(id):
    visitor = Visitor.query.get_or_404(id)
    visitor.status = 'Ushered'
    db.session.commit()
    return jsonify({'message': 'Visitor ushered successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)