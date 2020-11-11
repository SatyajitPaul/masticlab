from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin
import datetime
import json
from datetime import timedelta


class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///masticlab.sqlite'    # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning

    # Flask-User settings
    USER_APP_NAME = "MasticLab"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False      # Disable email authentication
    USER_ENABLE_USERNAME = True    # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False    # Simplify register form


def create_app():
    """ Flask application factory """
    
    # Create Flask app load app.config
    app = Flask(__name__)
    app.config.from_object(__name__+'.ConfigClass')

    # Initialize Flask-SQLAlchemy
    db = SQLAlchemy(app)

    # Define the User data-model.
    # NB: Make sure to add flask_user UserMixin !!!
    class User(db.Model, UserMixin):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

        # User authentication information. The collation='NOCASE' is required
        # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
        username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
        password = db.Column(db.String(255), nullable=False, server_default='')
        email_confirmed_at = db.Column(db.DateTime())

        # User information
        first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

    class Doctor(db.Model):
        __tablename__ = 'doctor'
        id = db.Column(db.Integer, primary_key=True)

        first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        phone_number = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        membership = db.Column('membership', db.Boolean(), nullable=False, server_default='0')
        address1 = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='NA')
        address2 = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='NA')
        state = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='Tripura')
        pincode = db.Column(db.String(6, collation='NOCASE'), nullable=False, server_default='000000')
        city = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        country = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='India')

        number_of_ref = db.Column(db.Integer)
        total_amount = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='00')



    class Patient(db.Model):
        __tablename__ = 'patient'
        id = db.Column(db.Integer, primary_key=True)

        first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        phone_number = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        gender = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        age = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='NA')
        address = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='NA')
        state = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='Tripura')
        pincode = db.Column(db.String(6, collation='NOCASE'), nullable=False, server_default='000000')
        city = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        country = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='India')

        number_of_visit = db.Column(db.Integer)
        total_biz = db.Column(db.Float)


    class Tests(db.Model):
        __tablename__ = 'tests'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        catagory = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        price = db.Column(db.Float)
        cost = db.Column(db.Float)
        done = db.Column(db.Integer)


    class Invoice(db.Model):
        __tablename__ = 'invoice'
        id = db.Column(db.Integer, primary_key=True)
        patient_id = db.Column(db.Integer)
        doctor_id = db.Column(db.Integer)
        created_date = db.Column(db.DateTime, default=datetime.datetime.now())
        number_of_test = db.Column(db.Integer)
        list_of_test = db.Column(db.String(1000, collation='NOCASE'), nullable=False, server_default='')
        total_amount = db.Column(db.Float)
        discount = db.Column(db.Float)
        current_payment = db.Column(db.Float)
        due_amount = db.Column(db.Float)
        test_status = db.Column('test_status', db.Boolean(), nullable=False, server_default='0')
        report_status = db.Column('report_status', db.Boolean(), nullable=False, server_default='0')
        report_id = db.Column(db.Integer)

    class Report(db.Model):
        __tablename__ = 'report'
        id = db.Column(db.Integer, primary_key=True)
        patient_id = db.Column(db.Integer)
        doctor_id = db.Column(db.Integer)
        invoice_id = db.Column(db.Integer)
        created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow) 
        data_of_test = db.Column(db.String(1000, collation='NOCASE'), nullable=False, server_default='')
        delivery_status = db.Column('delivery_status', db.Boolean(), nullable=False, server_default='0')


    class Pathology(db.Model):
        __tablename__ = 'pathology'
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='Test Name')
        min_val = db.Column(db.Float)
        max_val = db.Column(db.Float)
        unit = db.Column(db.String(10, collation='NOCASE'), nullable=False, server_default='Unit')
        



    # Create all database tables
    db.create_all()

    # Setup Flask-User and specify the User data-model
    user_manager = UserManager(app, db, User)

    # The Home page is accessible to anyone
    @app.route('/')
    def home_page():
        # String-based templates
        return render_template("index.html")


    @app.route('/invoice',methods = ['POST', 'GET'])
    def invoice():
        if request.method == 'POST':
            patient = request.form['patient']
            doctor = request.form['doctor']
            test = request.form['test']
            url_to_go = '/invoice/'+doctor+'/'+patient+'/'+test
            return redirect(url_to_go)
        # String-based templates

        else:
            return render_template("invoice.html" ,doctor = Doctor.query.all(), patient = Patient.query.all())

    @app.route('/invoice/<doctor>/<patient>/<test>',methods = ['POST', 'GET'])
    def invoiceGen(doctor, patient, test):
        # String-based templates
        patient = Patient.query.filter_by(id=patient).first_or_404()
        doctor = Doctor.query.filter_by(id=doctor).first_or_404()
        if request.method == 'POST':
            patient_id = int(patient.id)
            doctor_id = int(doctor.id)
            number_of_test = int(test)
            discount = float(request.form['discount'])
            current_payment = float(request.form['pay'])
            total_amount = 00.00

            testList = []
            for t in range(int(test)):
                testId = 'test-'+str(t)
                testValu = request.form[testId]
                testList.append(testValu)
                test_details = Tests.query.filter_by(id=testValu).first_or_404()
                test_price = float(test_details.price)
                total_amount += test_price

            testList = json.dumps(testList)

            due_amount = total_amount - ((total_amount * discount)/100) - current_payment

            print(due_amount)
            print("*****")
            inv = Invoice(patient_id = patient_id, doctor_id = doctor_id, number_of_test = number_of_test, list_of_test = str(testList), total_amount = total_amount, discount = discount, current_payment = current_payment, due_amount = due_amount)
            db.session.add(inv)
            db.session.commit()
            return redirect(url_for('allInvoice'))

        else:
            return render_template("invoiceGen.html", test=int(test), tests = Tests.query.all(), patient = patient, doctor = doctor)


    @app.route('/add-doctor',methods = ['POST', 'GET'])
    def addDoctore():
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            phone = request.form['phone']
            membership = bool(request.form['membership'])
            address1 = request.form['adress1']
            address2 = request.form['adress2']
            state = request.form['state']
            postcode = request.form['postcode']
            city = request.form['city']
            country = request.form['country']
            print(country)

            doctor = Doctor(first_name=fname, last_name = lname, phone_number = phone, membership = membership, address1 = address1, address2 = address2, state=state,pincode=postcode, city=city, country=country, number_of_ref=0, total_amount='00.00')
            db.session.add(doctor)
            db.session.commit()
            
            return redirect(url_for('listDoctor'))
        else:
            return render_template("addDoctore.html")

    @app.route('/list-doctor')
    def listDoctor():
        return render_template("listDoctore.html", doctor = Doctor.query.all())

    @app.route('/list-test')
    def listTest():
        return render_template("listTest.html", tests = Tests.query.all())

    @app.route('/list-patient')
    def listPatient():
        return render_template("listPatient.html", patient = Patient.query.all())

    @app.route('/all-invoice')
    def allInvoice():
        return render_template("allInvoice.html", invoice = Invoice.query.all())

    @app.route('/test-done/<invoice>')
    def testDone(invoice):
        inv = Invoice.query.filter_by(id=invoice).first_or_404()
        inv.test_status = True
        db.session.commit()
        return redirect('/view-invoice/'+invoice)

    @app.route('/print/<invoice>')
    def printInvoice(invoice):
        inv = Invoice.query.filter_by(id=invoice).first_or_404()
        doc = Doctor.query.filter_by(id=inv.doctor_id).first_or_404()
        pat = Patient.query.filter_by(id=inv.patient_id).first_or_404()
        delivery = inv.created_date + timedelta(days = 5)
        n = inv.number_of_test
        listOfTest = inv.list_of_test
        listOfTest = json.loads(listOfTest)
        testName = []
        testCode = []
        testProfile = []
        testPrice = []
        for test in listOfTest:
            getTest = Tests.query.filter_by(id=test).first_or_404()
            testName.append(getTest.name)
            testCode.append("AD"+str(1000+getTest.id))
            testProfile.append(getTest.catagory)
            testPrice.append(getTest.price)

        return render_template("print.html", inv = inv, pat = pat, doc = doc, n = n, testName = testName, testCode = testCode, testProfile = testProfile, testPrice = testPrice, d = delivery)




    @app.route('/view-invoice/<invoice>')
    def viewInvoice(invoice):
        inv = Invoice.query.filter_by(id=invoice).first_or_404()
        doc = Doctor.query.filter_by(id=inv.doctor_id).first_or_404()
        pat = Patient.query.filter_by(id=inv.patient_id).first_or_404()
        n = inv.number_of_test
        listOfTest = inv.list_of_test
        listOfTest = json.loads(listOfTest)
        print(type(listOfTest))
        nameOfTest = []
        for test in listOfTest:
            getTest = Tests.query.filter_by(id=test).first_or_404()
            nameOfTest.append(getTest.name)
        print(nameOfTest)
        return render_template("viewInvoice.html", inv = inv, doc = doc, pat = pat, test = nameOfTest, n = n)

    @app.route('/add-patient',methods = ['POST', 'GET'])
    def addPatient():
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            phone = request.form['phone']
            gender = request.form['gender']
            age = request.form['ageValue'] + request.form['age']
            address = request.form['adress']
            state = request.form['state']
            postcode = request.form['postcode']
            city = request.form['city']
            country = request.form['country']
            print(country)

            patient = Patient(first_name=fname, last_name = lname, phone_number = phone, gender = gender, age = age, address = address, state=state,pincode=postcode, city=city, country=country, number_of_visit = 1, total_biz = 00.00 )
            db.session.add(patient)
            db.session.commit()
            
            return redirect(url_for('listPatient'))
        else:
            return render_template("addPatient.html")

    @app.route('/add-test',methods = ['POST', 'GET'])
    def addTest():
        if request.method == 'POST':
            name = request.form['name']
            catagory = request.form['catagory']
            price = float(request.form['price'])
            price = format(price, '.2f')
            cost = format(float(request.form['cost']), '.2f')
            print(price)
            print('#####')

            test = Tests(name = name, catagory = catagory, price = price, cost = cost, done = 0)
            db.session.add(test)
            db.session.commit()

            return redirect(url_for('listTest'))

        else:
            return render_template("addTest.html")

    # The Members page is only accessible to authenticated users via the @login_required decorator
    @app.route('/members')
    @login_required    # User must be authenticated
    def member_page():
        # String-based templates
        return render_template("index.html")

    return app


# Start development web server
if __name__=='__main__':
    app = create_app()
    app.run(debug=True)