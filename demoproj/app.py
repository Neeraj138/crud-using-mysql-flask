from flask import Flask, render_template, url_for, redirect, request, flash
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'pranay'
app.config['MYSQL_DB'] = 'genetic'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

app.secret_key = "jkjldjls"

mysql = MySQL(app)

@app.route("/")
def home():
    conn = mysql.connection.cursor()
    sql_query = "select * from research"
    conn.execute(sql_query)
    res = conn.fetchall()
    return render_template("home.html",researches=res)

@app.route("/addResearch",methods=['GET','POST'])
def addResearch():
    if request.method=='POST':
        budget = request.form['budget']
        team_name = request.form['team_name']
        start_date = request.form['start_date']
        papers_published = request.form['papers_published']
        conn = mysql.connection.cursor()
        sql_query = "insert into research (budget, team_name, start_date, papers_published) values (%s,%s,%s,%s)"
        conn.execute(sql_query,[budget,team_name,start_date,papers_published])
        mysql.connection.commit()
        conn.close()
        flash("Added new project")
        return redirect(url_for('home'))
    return render_template("addResearch.html")

@app.route("/updateResearch/<string:rid>",methods=['GET','POST'])
def updateResearch(rid):
    conn = mysql.connection.cursor()
    if request.method=='POST':
        budget = request.form['budget']
        team_name = request.form['team_name']
        start_date = request.form['start_date']
        papers_published = request.form['papers_published']
        sql_query = "update research set budget=%s,team_name=%s,start_date=%s,papers_published=%s where rid=%s"
        conn.execute(sql_query,[budget,team_name,start_date,papers_published,rid])
        mysql.connection.commit()
        conn.close()
        flash("Updated!!!")
        return redirect(url_for('home'))
    sql_query = "select * from research where rid=%s"
    conn.execute(sql_query,[rid])
    res = conn.fetchone()
    return render_template("updateResearch.html",values=res)

@app.route("/deleteResearch/<string:rid>",methods=['GET','POST'])
def deleteResearch(rid):
    conn = mysql.connection.cursor()
    sql_query = "delete from research where rid=%s"
    conn.execute(sql_query,[rid])
    mysql.connection.commit()
    conn.close()
    flash("deleted!!!")
    return redirect(url_for('home'))

@app.route("/showResearch/<string:rid>",methods=['GET','POST'])
def showResearch(rid):
    return render_template("showResearch.html",value=rid)

@app.route("/showPeople/<string:rid>",methods=['GET','POST'])
def showPeople(rid):
    conn = mysql.connection.cursor()
    sql_query = "select * from people where people_id in (select people_id from involves where rid=%s)"
    conn.execute(sql_query,[rid])
    res = conn.fetchall()
    return render_template("showPeople.html",people=res,value=rid)

@app.route("/addPeople/<string:rid>",methods=['GET','POST'])
def addPeople(rid):
    if request.method=='POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        role = request.form['role']
        conn = mysql.connection.cursor()
        sql_query = "insert into people (name,age,gender) values (%s,%s,%s)"
        conn.execute(sql_query,[name,age,gender])
        mysql.connection.commit()
        sql_query = "select last_insert_id()"
        conn.execute(sql_query)
        person_id = conn.fetchone()['last_insert_id()']
        sql_query = "insert into involves values(%s,%s)"
        conn.execute(sql_query,[rid,person_id])
        mysql.connection.commit()
        conn.close()
        if role=="Funder":
            return redirect(url_for('addFunderDetails',people_id=person_id,rid=rid))
        if role=="Patient":
            return redirect(url_for('addPatientDetails',people_id=person_id,rid=rid))
        if role=="Scientist":
            return redirect(url_for('addScientistDetails',people_id=person_id,rid=rid))
        if role=="Intern":
            return redirect(url_for('addInternDetails',people_id=person_id,rid=rid))  
        flash("Added new person")
        return redirect(url_for('showPeople',rid=rid))
    return render_template("addPeople.html",value=rid)

@app.route("/showScientists/<string:rid>",methods=['GET','POST'])
def showScientists(rid):
    conn = mysql.connection.cursor()
    sql_query = f'''
    select scientist.id, scientist.sid, people.name, scientist.specialization,scientist.salary from research
    inner join involves on research.rid = involves.rid
    inner join people on people.people_id = involves.people_id
    inner join scientist on scientist.id = people.people_id
    where research.rid = %s;
    '''
    conn.execute(sql_query,[rid])
    res = conn.fetchall()
    return render_template("showScientists.html",people=res,value=rid)

@app.route("/showInterns/<string:rid>",methods=['GET','POST'])
def showInterns(rid):
    conn = mysql.connection.cursor()
    sql_query = f'''
    select intern.id, intern.iid, people.name,people.age,people.gender, intern.stipend from research
    inner join involves on research.rid = involves.rid
    inner join people on people.people_id = involves.people_id
    inner join intern on intern.id = people.people_id
    where research.rid = %s;
    '''
    conn.execute(sql_query,[rid])
    res = conn.fetchall()
    return render_template("showInterns.html",people=res,value=rid)

@app.route("/addScientist/<string:rid>",methods=['GET','POST'])
def addScientist(rid):
    if request.method=='POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        specialization = request.form['specialization']
        salary=request.form['salary']
        conn = mysql.connection.cursor()
        sql_query = "insert into people (name,age,gender) values (%s,%s,%s)"
        conn.execute(sql_query,[name,age,gender])
        mysql.connection.commit()
        sql_query = "select last_insert_id()"
        conn.execute(sql_query)
        person_id = conn.fetchone()['last_insert_id()']
        sql_query = "insert into involves values(%s,%s)"
        conn.execute(sql_query,[rid,person_id])
        mysql.connection.commit()
        sql_query = "insert into scientist(id,specialization,salary) values(%s,%s,%s)"
        conn.execute(sql_query,[person_id,specialization,salary])
        mysql.connection.commit()
        conn.close()
        flash("Added Scientist Details")
        return redirect(url_for('showScientists',rid=rid))
    return render_template("addScientist.html",value=rid)

@app.route("/addIntern/<string:rid>",methods=['GET','POST'])
def addIntern(rid):
    if request.method=='POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        stipend=request.form['stipend']
        conn = mysql.connection.cursor()
        sql_query = "insert into people (name,age,gender) values (%s,%s,%s)"
        conn.execute(sql_query,[name,age,gender])
        mysql.connection.commit()
        sql_query = "select last_insert_id()"
        conn.execute(sql_query)
        person_id = conn.fetchone()['last_insert_id()']
        sql_query = "insert into involves values(%s,%s)"
        conn.execute(sql_query,[rid,person_id])
        mysql.connection.commit()
        sql_query = "insert into intern(id,stipend) values(%s,%s)"
        conn.execute(sql_query,[person_id,stipend])
        mysql.connection.commit()
        conn.close()
        flash("Added Intern Details")
        return redirect(url_for('showInterns',rid=rid))
    return render_template("addIntern.html",value=rid)

@app.route("/addScientistDetails/<string:people_id>",methods=['GET','POST'])
def addScientistDetails(people_id):
    rid = request.args.get('rid',None)
    if request.method=='POST':
        specialization = request.form['specialization']
        salary = request.form['salary']
        conn = mysql.connection.cursor()
        sql_query = "insert into scientist(id,specialization,salary) values(%s,%s,%s)"
        conn.execute(sql_query,[people_id,specialization,salary])
        mysql.connection.commit()
        conn.close()
        flash("Added Scientist Details")
        return redirect(url_for('showPeople',rid=rid))
    return render_template("addScientistDetails.html")

@app.route("/addInternDetails/<string:people_id>",methods=['GET','POST'])
def addInternDetails(people_id):
    rid = request.args.get('rid',None)
    if request.method=='POST':
        stipend = request.form['stipend']
        conn = mysql.connection.cursor()
        sql_query = "insert into intern(id,stipend) values(%s,%s)"
        conn.execute(sql_query,[people_id,stipend])
        mysql.connection.commit()
        conn.close()
        flash("Added Intern Details")
        return redirect(url_for('showPeople',rid=rid))
    return render_template("addinternDetails.html")

@app.route("/updateScientist/<string:people_id>",methods=['GET','POST'])
def updateScientist(people_id):
    rid = request.args.get('rid',None)
    conn = mysql.connection.cursor()
    if request.method=='POST':
        specialization= request.form['specialization']
        salary = request.form['salary']
        sql_query = "update scientist set specialization=%s, salary=%s where id=%s"
        conn.execute(sql_query,[specialization,salary,people_id])
        mysql.connection.commit()
        conn.close()
        flash("Updated!!!")
        return redirect(url_for('showScientists',rid=rid))
    sql_query = "select * from scientist where id=%s"
    conn.execute(sql_query,[people_id])
    res = conn.fetchone()
    return render_template("updateScientist.html",values=res)

@app.route("/updateIntern/<string:people_id>",methods=['GET','POST'])
def updateIntern(people_id):
    rid = request.args.get('rid',None)
    conn = mysql.connection.cursor()
    if request.method=='POST':
        stipend= request.form['stipend']
        sql_query = "update intern set stipend=%s where id=%s"
        conn.execute(sql_query,[stipend,people_id])
        mysql.connection.commit()
        conn.close()
        flash("Updated!!!")
        return redirect(url_for('showInterns',rid=rid))
    sql_query = "select * from intern where id=%s"
    conn.execute(sql_query,[people_id])
    res = conn.fetchone()
    return render_template("updateIntern.html",values=res)

@app.route("/deleteScientist/<string:people_id>",methods=['GET','POST'])
def deleteScientist(people_id):
    rid = request.args.get('rid',None)
    conn = mysql.connection.cursor()
    sql_query = "delete from scientist where id=%s"
    conn.execute(sql_query,[people_id])
    mysql.connection.commit()
    conn.close()
    flash("deleted!!!")
    return redirect(request.referrer)

@app.route("/deleteIntern/<string:people_id>",methods=['GET','POST'])
def deleteIntern(people_id):
    rid = request.args.get('rid',None)
    conn = mysql.connection.cursor()
    sql_query = "delete from intern where id=%s"
    conn.execute(sql_query,[people_id])
    mysql.connection.commit()
    conn.close()
    flash("deleted!!!")
    return redirect(request.referrer)

@app.route("/addFunderDetails/<string:people_id>",methods=['GET','POST'])
def addFunderDetails(people_id):
    rid = request.args.get('rid',None)
    if request.method=='POST':
        amnt_funded = request.form['amnt_funded']
        date_of_funding = request.form['date_of_funding']
        conn = mysql.connection.cursor()
        sql_query = "insert into funder(id, amnt_funded, date_of_funding) values(%s,%s,%s)"
        conn.execute(sql_query,[people_id,amnt_funded,date_of_funding])
        mysql.connection.commit()
        conn.close()
        flash("Added Funder Details")
        return redirect(url_for('showPeople',rid=rid))
    return render_template("addFunderDetails.html")

@app.route("/addPatientDetails/<string:people_id>",methods=['GET','POST'])
def addPatientDetails(people_id):
    rid = request.args.get('rid',None)
    if request.method=='POST':
        locality = request.form['locality']
        city = request.form['city']
        zip = request.form['zip']
        state = request.form['state']
        country = request.form['country']
        conn = mysql.connection.cursor()
        sql_query = "insert into patient(id,locality,city,zip,state,country) values(%s,%s,%s,%s,%s,%s)"
        conn.execute(sql_query,[people_id,locality,city,zip,state,country])
        mysql.connection.commit()
        conn.close()
        flash("Added Patient Details")
        return redirect(url_for('showPeople',rid=rid))
    return render_template("addPatientDetails.html")

@app.route("/addPatient/<string:rid>",methods=['GET','POST'])
def addPatient(rid):
    if request.method=='POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        locality = request.form['locality']
        city = request.form['city']
        zip = request.form['zip']
        state = request.form['state']
        country = request.form['country']
        conn = mysql.connection.cursor()
        sql_query = "insert into people (name,age,gender) values (%s,%s,%s)"
        conn.execute(sql_query,[name,age,gender])
        mysql.connection.commit()
        sql_query = "select last_insert_id()"
        conn.execute(sql_query)
        person_id = conn.fetchone()['last_insert_id()']
        sql_query = "insert into involves values(%s,%s)"
        conn.execute(sql_query,[rid,person_id])
        mysql.connection.commit()
        sql_query = "insert into patient(id,locality,city,zip,state,country) values(%s,%s,%s,%s,%s,%s)"
        conn.execute(sql_query,[person_id,locality,city,zip,state,country])
        mysql.connection.commit()
        conn.close()
        flash("Added Patient Details")
        return redirect(url_for('showPatients',rid=rid))
    return render_template("addPatient.html",value=rid)

@app.route("/showFunders/<string:rid>",methods=['GET','POST'])
def showFunders(rid):
    conn = mysql.connection.cursor()
    sql_query = f'''
    select funder.id, people.name, funder.transaction_id, funder.amnt_funded, funder.date_of_funding from research
    inner join involves on research.rid = involves.rid
    inner join people on people.people_id = involves.people_id
    inner join funder on funder.id = people.people_id
    where research.rid = %s;
    '''
    conn.execute(sql_query,[rid])
    res = conn.fetchall()
    return render_template("showFunders.html",people=res,value=rid)

@app.route("/showPatients/<string:rid>",methods=['GET','POST'])
def showPatients(rid):
    conn = mysql.connection.cursor()
    sql_query = f'''
    select patient.id, patient.pid, people.name, people.age, people.gender, patient.locality, patient.city, patient.zip, patient.state, patient.country from research
    inner join involves on research.rid = involves.rid
    inner join people on people.people_id = involves.people_id
    inner join patient on patient.id = people.people_id
    where research.rid = %s;
    '''
    conn.execute(sql_query,[rid])
    res = conn.fetchall()
    return render_template("showPatients.html",people=res,value=rid)

@app.route("/showSamples/<string:people_id>",methods=['GET','POST'])
def showSamples(people_id):
    conn = mysql.connection.cursor()
    rid = request.args.get('rid',None)
    sql_query = "select * from sample where id=%s"
    conn.execute(sql_query,[people_id])
    res = conn.fetchall()
    return render_template("showSamples.html",samples=res,person_id=people_id,rid=rid)

@app.route("/showSequences/<string:sam_id>",methods=['GET','POST'])
def showSequences(sam_id):
    conn = mysql.connection.cursor()
    rid = request.args.get('rid',None)
    people_id = request.args.get('people_id')
    sql_query = "select * from sequence where sam_id=%s"
    conn.execute(sql_query,[sam_id])
    res = conn.fetchall()
    return render_template("showSequences.html",sequences=res,people_id=people_id,rid=rid,sam_id=sam_id)

@app.route("/addSample/<string:people_id>",methods=['GET','POST'])
def addSample(people_id):
    rid = request.args.get('rid',None)
    if request.method=='POST':
        date_col = request.form['date_col']
        body_part = request.form['body_part']
        conn = mysql.connection.cursor()
        sql_query = "insert into sample(id, date_col, body_part) values(%s,%s,%s)"
        conn.execute(sql_query,[people_id,date_col,body_part])
        mysql.connection.commit()
        conn.close()
        flash("Added Sample Details")
        return redirect(url_for('showSamples',people_id=people_id,rid=rid))
    return render_template("addSample.html",people_id=people_id)

@app.route("/addSequence/<string:sam_id>",methods=['GET','POST'])
def addSequence(sam_id):
    rid = request.args.get('rid',None)
    people_id = request.args.get('people_id')
    if request.method=='POST':
        conn = mysql.connection.cursor()
        length_seq = request.form['length_seq']
        dna_seq = request.form['dna_seq']
        genome_region = request.form['genome_region']
        sql_query = "insert into sequence(sam_id,length_seq,dna_seq,genome_region) values(%s,%s,%s,%s)"
        conn.execute(sql_query,[sam_id,length_seq,dna_seq,genome_region])
        mysql.connection.commit()
        conn.close()
        flash("Added Sequence Details")
        return redirect(url_for('showSequences',sam_id=sam_id,rid=rid,people_id=people_id))
    return render_template("addSequence.html",sam_id=sam_id)

@app.route("/updateSample/<string:sam_id>",methods=['GET','POST'])
def updateSample(sam_id):
    conn = mysql.connection.cursor()
    rid = request.args.get('rid',None)
    people_id = request.args.get('people_id',None)
    if request.method=='POST':
        date_col = request.form['date_col']
        body_part = request.form['body_part']
        sql_query = "update sample set date_col=%s, body_part=%s where sam_id=%s"
        conn.execute(sql_query,[date_col,body_part,sam_id])
        mysql.connection.commit()
        conn.close()
        flash("Updated Sample Details")
        return redirect(url_for('showSamples',people_id=people_id,rid=rid))
    sql_query = "select * from sample where sam_id=%s"
    conn.execute(sql_query,[people_id])
    res = conn.fetchone()
    return render_template("updateSample.html",values=res,sam_id=sam_id)

@app.route("/updateSequence/<string:seq_id>",methods=['GET','POST'])
def updateSequence(seq_id):
    conn = mysql.connection.cursor()
    rid = request.args.get('rid',None)
    people_id = request.args.get('people_id',None)
    sam_id = request.args.get('sam_id',None)
    if request.method=='POST':
        length_seq = request.form['length_seq']
        dna_seq = request.form['dna_seq']
        genome_region = request.form['genome_region']
        sql_query = "update sequence set length_seq=%s, dna_seq=%s, genome_region=%s where seq_id=%s"
        conn.execute(sql_query,[length_seq,dna_seq,genome_region,seq_id])
        mysql.connection.commit()
        conn.close()
        flash("Updated Sequence Details")
        return redirect(url_for('showSequences',sam_id=sam_id,rid=rid,people_id=people_id))
    sql_query = "select * from sequence where seq_id=%s"
    conn.execute(sql_query,[seq_id])
    res = conn.fetchone()
    return render_template("updateSequence.html",values=res,seq_id=seq_id)

@app.route("/deleteSample/<string:sam_id>",methods=['GET','POST'])
def deleteSample(sam_id):
    conn = mysql.connection.cursor()
    sql_query = "delete from sample where sam_id=%s"
    conn.execute(sql_query,[sam_id])
    mysql.connection.commit()
    conn.close()
    flash("deleted!!!")
    return redirect(request.referrer)

@app.route("/deleteSequence/<string:seq_id>",methods=['GET','POST'])
def deleteSequence(seq_id):
    conn = mysql.connection.cursor()
    sql_query = "delete from sequence where seq_id=%s"
    conn.execute(sql_query,[seq_id])
    mysql.connection.commit()
    conn.close()
    flash("deleted!!!")
    return redirect(request.referrer)

@app.route("/updatePeople/<string:people_id>",methods=['GET','POST'])
def updatePeople(people_id):
    conn = mysql.connection.cursor()
    rid = request.args.get('rid',None)
    if request.method=='POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        sql_query = "update people set name=%s,age=%s,gender=%s where people_id=%s"
        conn.execute(sql_query,[name,age,gender,people_id])
        mysql.connection.commit()
        conn.close()
        flash("Updated!!!")
        return redirect(url_for('showPeople',rid=rid))
    sql_query = "select * from people where people_id=%s"
    conn.execute(sql_query,[people_id])
    res = conn.fetchone()
    return render_template("updatePeople.html",values=res)

@app.route("/updateFunder/<string:people_id>",methods=['GET','POST'])
def updateFunder(people_id):
    rid = request.args.get('rid',None)
    tid = request.args.get('tranid',None)
    conn = mysql.connection.cursor()
    if request.method=='POST':
        amnt_funded = request.form['amnt_funded']
        date_of_funding = request.form['date_of_funding']
        sql_query = "update funder set amnt_funded=%s, date_of_funding=%s where id=%s and transaction_id=%s"
        conn.execute(sql_query,[amnt_funded,date_of_funding,people_id,tid])
        mysql.connection.commit()
        conn.close()
        flash("Updated!!!")
        return redirect(url_for('showFunders',rid=rid))
    sql_query = "select * from funder where id=%s and transaction_id=%s"
    conn.execute(sql_query,[people_id,tid])
    res = conn.fetchone()
    return render_template("updateFunder.html",values=res,tid=tid)

@app.route("/updatePatient/<string:people_id>",methods=['GET','POST'])
def updatePatient(people_id):
    rid = request.args.get('rid',None)
    conn = mysql.connection.cursor()
    if request.method=='POST':
        locality = request.form['locality']
        city = request.form['city']
        zip = request.form['zip']
        state = request.form['state']
        country = request.form['country']
        sql_query = "update patient set locality=%s, city=%s, zip=%s, state=%s, country=%s  where id=%s"
        conn.execute(sql_query,[locality,City,zip,state,country,people_id])
        mysql.connection.commit()
        conn.close()
        flash("Updated!!!")
        return redirect(url_for('showPatients',rid=rid))
    sql_query = "select * from patient where id=%s"
    conn.execute(sql_query,[people_id])
    res = conn.fetchone()
    return render_template("updatePatient.html",values=res)

@app.route("/addFunder/<string:rid>",methods=['GET','POST'])
def addFunder(rid):
    if request.method=='POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        amnt_funded = request.form['amnt_funded']
        date_of_funding = request.form['date_of_funding']
        conn = mysql.connection.cursor()
        sql_query = "insert into people (name,age,gender) values (%s,%s,%s)"
        conn.execute(sql_query,[name,age,gender])
        mysql.connection.commit()
        sql_query = "select last_insert_id()"
        conn.execute(sql_query)
        person_id = conn.fetchone()['last_insert_id()']
        sql_query = "insert into involves values(%s,%s)"
        conn.execute(sql_query,[rid,person_id])
        mysql.connection.commit()
        sql_query = "insert into funder(id, amnt_funded, date_of_funding) values(%s,%s,%s)"
        conn.execute(sql_query,[person_id,amnt_funded,date_of_funding])
        mysql.connection.commit()
        conn.close()
        flash("Added Funder Details")
        return redirect(url_for('showFunders',rid=rid))
    return render_template("addFunder.html",value=rid)



@app.route("/deletePeople/<string:people_id>",methods=['GET','POST'])
def deletePeople(people_id):
    conn = mysql.connection.cursor()
    rid = request.args.get('rid',None)
    sql_query = "delete from people where people_id=%s"
    conn.execute(sql_query,[people_id])
    mysql.connection.commit()
    conn.close()
    flash("deleted!!!")
    return redirect(request.referrer)

@app.route("/deleteFunder/<string:people_id>",methods=['GET','POST'])
def deleteFunder(people_id):
    rid = request.args.get('rid',None)
    tid = request.args.get('tranid',None)
    conn = mysql.connection.cursor()
    sql_query = "delete from funder where id=%s and transaction_id=%s"
    conn.execute(sql_query,[people_id,tid])
    mysql.connection.commit()
    conn.close()
    flash("deleted!!!")
    return redirect(request.referrer)

@app.route("/deletePatient/<string:people_id>",methods=['GET','POST'])
def deletePatient(people_id):
    rid = request.args.get('rid',None)
    conn = mysql.connection.cursor()
    sql_query = "delete from patient where id=%s"
    conn.execute(sql_query,[people_id])
    mysql.connection.commit()
    conn.close()
    flash("deleted!!!")
    return redirect(request.referrer)

if(__name__=='__main__'):
    app.run(debug=True)
