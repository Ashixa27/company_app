from flask import Flask, request, jsonify
import company_func as db
from flask_httpauth import HTTPBasicAuth
from auth_data import users, ALLOWED_IPS, db_config

app= Flask(__name__)

auth = HTTPBasicAuth()


@app.before_request
def limit_remote_ips():
    client_ip = request.remote_addr
    if client_ip not in ALLOWED_IPS:
        return jsonify({"error": "You are not allowed"}), 403


@auth.verify_password
def verify_password(username, password):
    if username in users:
        if password == users['username']:
            return True
    return False


@app.route("/")
def first_func():
    print("Sunt aici")
    return {"message": "Ran successfully"}


@app.route("/test", methods=['GET','PUT'])
def test_func():
    if request.method == 'GET':
        return {"message": "Successful GET request"}
    return {"message": f"Successful PUT request -> body sent {request.data}"}


@app.route("/emps")
def get_all_employees():
    try:
        response = request.json
    except Exception as e:
        response = None
        
    if response:
        query = f"select * from company.employees where {list(response.keys()[0])} = '{list(response.values()[0])}'"
    else:
        query = "select * from company.employees"
    emps = db.read_from_db(query, db_config)
    return emps


@app.route("/emps", methods=['POST'])
def add_employee():
    data = request.json
    if data:
        query = f"""select department_id, budget from company.departments where department_name = '{data['department_name']}'"""
        department = db.read_from_db(query, db_config)
        if "error" in str(department):
            return {"error": "Department does not exist"}
        department_id = int(department[0]['department_id'])
        department_budget = int(department[0]['budget'])
        query = f"select SUM(salary) as suma from company.employees e where department_id= {department_id};"
        total_salaries = db.read_from_db(query, db_config)
        total_salaries = total_salaries[0]['suma']
        if data['salary'] + total_salaries > department_budget:
            return {"error": "Salary is to expensive fore department's budget"}
        query = ("insert into company.employees(emp_cnp, emp_name, birth_date, department_id, salary) "
                 f"values ('{data['cnp']}','{data['name']}','{data['birth_date']}',{department_id},{data['salary']})")
        response = db.execute_query(query, db_config)
        if response:
            return {"message": "Employee added successfully"}
        else:
            return {"error": f"Unsuccessful execution {response}"}
    else:
        return {"error": "No data given"}


@app.route("/emps", methods=['DELETE'])
@auth.login_required
def fire_employee():
    name = request.args.get('name', "")
    query = f"""DELETE from company.employees where emp_name = {name}"""
    ok, response = db.execute_query(query,db_config)
    if ok:
        if "DELETE 0" in response:
            return {"message": "Employee not deleted"}
        else:
            return {"message": "Employee was fired"}
    else:
        return {"error": f"exception {response}"}


@app.route("/departments")
def get_departments():
    try:
        name = request.args.get('name', "")
        if name:
            query = f"select * from company.departments where department_name='{name}'"
        else:
            query = "select * from company.departments"

        depts = db.read_from_db(query, db_config)
        return depts

    except Exception as e:
        print(e)
        return {}


@app.route("/projects")
def get_projects():
    try:
        project_id = request.args.get('project_id', "")
        if project_id:
            query = f"select * from company.projects where project_id={project_id}"
        else:
            query = "select * from company.projects"

        depts = db.read_from_db(query, db_config)
        return depts

    except Exception as e:
        print(e)
        return {}


if __name__ == '__main__':
    app.run()