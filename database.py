import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'job_tracker'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            port=int(os.getenv('DB_PORT', 3306)),
            unix_socket='/tmp/mysql.sock'
        )
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        raise e

def execute_query(query, params=None, fetch=False, fetch_one=False):
    """Execute a query and optionally return results."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch:
            result = cursor.fetchall()
        else:
            connection.commit()
            result = cursor.lastrowid
        
        return result
    except Error as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# --- Dashboard Queries ---
def get_dashboard_stats():
    stats = {}
    stats['total_companies'] = execute_query("SELECT COUNT(*) as c FROM companies", fetch_one=True)['c']
    stats['total_jobs'] = execute_query("SELECT COUNT(*) as c FROM jobs", fetch_one=True)['c']
    stats['total_applications'] = execute_query("SELECT COUNT(*) as c FROM applications", fetch_one=True)['c']
    stats['total_contacts'] = execute_query("SELECT COUNT(*) as c FROM contacts", fetch_one=True)['c']
    
    stats['status_counts'] = execute_query("""
        SELECT status, COUNT(*) as count FROM applications GROUP BY status
    """, fetch=True)
    
    stats['recent_applications'] = execute_query("""
        SELECT a.*, j.job_title, c.company_name
        FROM applications a
        LEFT JOIN jobs j ON a.job_id = j.job_id
        LEFT JOIN companies c ON j.company_id = c.company_id
        ORDER BY a.application_date DESC LIMIT 5
    """, fetch=True)
    
    stats['offers'] = execute_query("SELECT COUNT(*) as c FROM applications WHERE status='Offer'", fetch_one=True)['c']
    stats['interviews'] = execute_query("SELECT COUNT(*) as c FROM applications WHERE status='Interview'", fetch_one=True)['c']
    
    return stats

# --- Companies CRUD ---
def get_all_companies():
    return execute_query("""
        SELECT c.*, COUNT(DISTINCT j.job_id) as job_count, COUNT(DISTINCT co.contact_id) as contact_count
        FROM companies c
        LEFT JOIN jobs j ON c.company_id = j.company_id
        LEFT JOIN contacts co ON c.company_id = co.company_id
        GROUP BY c.company_id
        ORDER BY c.company_name
    """, fetch=True)

def get_company(company_id):
    return execute_query("SELECT * FROM companies WHERE company_id = %s", (company_id,), fetch_one=True)

def create_company(data):
    return execute_query("""
        INSERT INTO companies (company_name, industry, website, city, state, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (data['company_name'], data.get('industry'), data.get('website'),
          data.get('city'), data.get('state'), data.get('notes')))

def update_company(company_id, data):
    execute_query("""
        UPDATE companies SET company_name=%s, industry=%s, website=%s, city=%s, state=%s, notes=%s
        WHERE company_id=%s
    """, (data['company_name'], data.get('industry'), data.get('website'),
          data.get('city'), data.get('state'), data.get('notes'), company_id))

def delete_company(company_id):
    execute_query("DELETE FROM companies WHERE company_id = %s", (company_id,))

# --- Jobs CRUD ---
def get_all_jobs():
    return execute_query("""
        SELECT j.*, c.company_name,
               COUNT(a.application_id) as application_count
        FROM jobs j
        LEFT JOIN companies c ON j.company_id = c.company_id
        LEFT JOIN applications a ON j.job_id = a.job_id
        GROUP BY j.job_id
        ORDER BY j.date_posted DESC
    """, fetch=True)

def get_job(job_id):
    return execute_query("""
        SELECT j.*, c.company_name FROM jobs j
        LEFT JOIN companies c ON j.company_id = c.company_id
        WHERE j.job_id = %s
    """, (job_id,), fetch_one=True)

def create_job(data):
    import json
    reqs = data.get('requirements', '[]')
    if isinstance(reqs, str):
        # Parse comma-separated skills into JSON array
        skills = [s.strip() for s in reqs.split(',') if s.strip()]
        reqs = json.dumps(skills)
    return execute_query("""
        INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, requirements)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (data.get('company_id'), data['job_title'], data.get('job_type'),
          data.get('salary_min') or None, data.get('salary_max') or None,
          data.get('job_url'), data.get('date_posted') or None, reqs))

def update_job(job_id, data):
    import json
    reqs = data.get('requirements', '[]')
    if isinstance(reqs, str):
        skills = [s.strip() for s in reqs.split(',') if s.strip()]
        reqs = json.dumps(skills)
    execute_query("""
        UPDATE jobs SET company_id=%s, job_title=%s, job_type=%s, salary_min=%s, salary_max=%s,
        job_url=%s, date_posted=%s, requirements=%s WHERE job_id=%s
    """, (data.get('company_id'), data['job_title'], data.get('job_type'),
          data.get('salary_min') or None, data.get('salary_max') or None,
          data.get('job_url'), data.get('date_posted') or None, reqs, job_id))

def delete_job(job_id):
    execute_query("DELETE FROM jobs WHERE job_id = %s", (job_id,))

# --- Applications CRUD ---
def get_all_applications():
    return execute_query("""
        SELECT a.*, j.job_title, c.company_name
        FROM applications a
        LEFT JOIN jobs j ON a.job_id = j.job_id
        LEFT JOIN companies c ON j.company_id = c.company_id
        ORDER BY a.application_date DESC
    """, fetch=True)

def get_application(app_id):
    return execute_query("""
        SELECT a.*, j.job_title, c.company_name FROM applications a
        LEFT JOIN jobs j ON a.job_id = j.job_id
        LEFT JOIN companies c ON j.company_id = c.company_id
        WHERE a.application_id = %s
    """, (app_id,), fetch_one=True)

def create_application(data):
    import json
    interview = data.get('interview_data', '{}')
    if isinstance(interview, str) and interview:
        try:
            json.loads(interview)
        except:
            interview = json.dumps({"notes": interview})
    elif not interview:
        interview = None
    return execute_query("""
        INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent, interview_data)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (data.get('job_id'), data['application_date'], data.get('status', 'Applied'),
          data.get('resume_version'), bool(data.get('cover_letter_sent')), interview))

def update_application(app_id, data):
    import json
    interview = data.get('interview_data', '{}')
    if isinstance(interview, str) and interview:
        try:
            json.loads(interview)
        except:
            interview = json.dumps({"notes": interview})
    elif not interview:
        interview = None
    execute_query("""
        UPDATE applications SET job_id=%s, application_date=%s, status=%s, resume_version=%s,
        cover_letter_sent=%s, interview_data=%s WHERE application_id=%s
    """, (data.get('job_id'), data['application_date'], data.get('status', 'Applied'),
          data.get('resume_version'), bool(data.get('cover_letter_sent')), interview, app_id))

def delete_application(app_id):
    execute_query("DELETE FROM applications WHERE application_id = %s", (app_id,))

# --- Contacts CRUD ---
def get_all_contacts():
    return execute_query("""
        SELECT co.*, c.company_name FROM contacts co
        LEFT JOIN companies c ON co.company_id = c.company_id
        ORDER BY co.contact_name
    """, fetch=True)

def get_contact(contact_id):
    return execute_query("""
        SELECT co.*, c.company_name FROM contacts co
        LEFT JOIN companies c ON co.company_id = c.company_id
        WHERE co.contact_id = %s
    """, (contact_id,), fetch_one=True)

def create_contact(data):
    return execute_query("""
        INSERT INTO contacts (company_id, contact_name, title, email, phone, linkedin_url, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (data.get('company_id'), data['contact_name'], data.get('title'),
          data.get('email'), data.get('phone'), data.get('linkedin_url'), data.get('notes')))

def update_contact(contact_id, data):
    execute_query("""
        UPDATE contacts SET company_id=%s, contact_name=%s, title=%s, email=%s,
        phone=%s, linkedin_url=%s, notes=%s WHERE contact_id=%s
    """, (data.get('company_id'), data['contact_name'], data.get('title'),
          data.get('email'), data.get('phone'), data.get('linkedin_url'), data.get('notes'), contact_id))

def delete_contact(contact_id):
    execute_query("DELETE FROM contacts WHERE contact_id = %s", (contact_id,))

# --- Job Match ---
def get_jobs_with_requirements():
    return execute_query("""
        SELECT j.*, c.company_name FROM jobs j
        LEFT JOIN companies c ON j.company_id = c.company_id
        WHERE j.requirements IS NOT NULL AND j.requirements != 'null'
    """, fetch=True)