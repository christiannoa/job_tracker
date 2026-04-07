from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import database as db
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# ── Helpers ──────────────────────────────────────────────────────────────────

def parse_requirements(req_json):
    """Parse requirements JSON field into a list."""
    if not req_json:
        return []
    if isinstance(req_json, list):
        return req_json
    try:
        return json.loads(req_json)
    except:
        return []

# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route('/')
def dashboard():
    stats = db.get_dashboard_stats()
    status_map = {s['status']: s['count'] for s in stats['status_counts']}
    return render_template('dashboard.html', stats=stats, status_map=status_map)

# ── Companies ─────────────────────────────────────────────────────────────────

@app.route('/companies')
def companies():
    companies = db.get_all_companies()
    return render_template('companies.html', companies=companies)

@app.route('/companies/add', methods=['GET', 'POST'])
def add_company():
    if request.method == 'POST':
        try:
            db.create_company(request.form)
            flash('Company added successfully!', 'success')
            return redirect(url_for('companies'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return render_template('company_form.html', company=None, action='Add')

@app.route('/companies/edit/<int:company_id>', methods=['GET', 'POST'])
def edit_company(company_id):
    company = db.get_company(company_id)
    if not company:
        flash('Company not found.', 'danger')
        return redirect(url_for('companies'))
    if request.method == 'POST':
        try:
            db.update_company(company_id, request.form)
            flash('Company updated successfully!', 'success')
            return redirect(url_for('companies'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return render_template('company_form.html', company=company, action='Edit')

@app.route('/companies/delete/<int:company_id>', methods=['POST'])
def delete_company(company_id):
    try:
        db.delete_company(company_id)
        flash('Company deleted.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('companies'))

# ── Jobs ──────────────────────────────────────────────────────────────────────

@app.route('/jobs')
def jobs():
    jobs = db.get_all_jobs()
    for job in jobs:
        job['requirements_list'] = parse_requirements(job.get('requirements'))
    return render_template('jobs.html', jobs=jobs)

@app.route('/jobs/add', methods=['GET', 'POST'])
def add_job():
    companies = db.get_all_companies()
    if request.method == 'POST':
        try:
            db.create_job(request.form)
            flash('Job added successfully!', 'success')
            return redirect(url_for('jobs'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return render_template('job_form.html', job=None, companies=companies, action='Add')

@app.route('/jobs/edit/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    job = db.get_job(job_id)
    companies = db.get_all_companies()
    if not job:
        flash('Job not found.', 'danger')
        return redirect(url_for('jobs'))
    if request.method == 'POST':
        try:
            db.update_job(job_id, request.form)
            flash('Job updated successfully!', 'success')
            return redirect(url_for('jobs'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    job['requirements_str'] = ', '.join(parse_requirements(job.get('requirements')))
    return render_template('job_form.html', job=job, companies=companies, action='Edit')

@app.route('/jobs/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    try:
        db.delete_job(job_id)
        flash('Job deleted.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('jobs'))

# ── Applications ──────────────────────────────────────────────────────────────

@app.route('/applications')
def applications():
    apps = db.get_all_applications()
    return render_template('applications.html', applications=apps)

@app.route('/applications/add', methods=['GET', 'POST'])
def add_application():
    jobs = db.get_all_jobs()
    if request.method == 'POST':
        try:
            db.create_application(request.form)
            flash('Application added successfully!', 'success')
            return redirect(url_for('applications'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return render_template('application_form.html', application=None, jobs=jobs, action='Add')

@app.route('/applications/edit/<int:app_id>', methods=['GET', 'POST'])
def edit_application(app_id):
    application = db.get_application(app_id)
    jobs = db.get_all_jobs()
    if not application:
        flash('Application not found.', 'danger')
        return redirect(url_for('applications'))
    if request.method == 'POST':
        try:
            db.update_application(app_id, request.form)
            flash('Application updated!', 'success')
            return redirect(url_for('applications'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return render_template('application_form.html', application=application, jobs=jobs, action='Edit')

@app.route('/applications/delete/<int:app_id>', methods=['POST'])
def delete_application(app_id):
    try:
        db.delete_application(app_id)
        flash('Application deleted.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('applications'))

# ── Contacts ──────────────────────────────────────────────────────────────────

@app.route('/contacts')
def contacts():
    contacts = db.get_all_contacts()
    return render_template('contacts.html', contacts=contacts)

@app.route('/contacts/add', methods=['GET', 'POST'])
def add_contact():
    companies = db.get_all_companies()
    if request.method == 'POST':
        try:
            db.create_contact(request.form)
            flash('Contact added successfully!', 'success')
            return redirect(url_for('contacts'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return render_template('contact_form.html', contact=None, companies=companies, action='Add')

@app.route('/contacts/edit/<int:contact_id>', methods=['GET', 'POST'])
def edit_contact(contact_id):
    contact = db.get_contact(contact_id)
    companies = db.get_all_companies()
    if not contact:
        flash('Contact not found.', 'danger')
        return redirect(url_for('contacts'))
    if request.method == 'POST':
        try:
            db.update_contact(contact_id, request.form)
            flash('Contact updated!', 'success')
            return redirect(url_for('contacts'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return render_template('contact_form.html', contact=contact, companies=companies, action='Edit')

@app.route('/contacts/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    try:
        db.delete_contact(contact_id)
        flash('Contact deleted.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('contacts'))

# ── Job Match ─────────────────────────────────────────────────────────────────

@app.route('/job-match', methods=['GET', 'POST'])
def job_match():
    results = []
    user_skills = ''
    if request.method == 'POST':
        user_skills = request.form.get('skills', '')
        skill_list = [s.strip().lower() for s in user_skills.split(',') if s.strip()]
        all_jobs = db.get_jobs_with_requirements()
        
        for job in all_jobs:
            job_reqs = parse_requirements(job.get('requirements'))
            job_reqs_lower = [r.lower() for r in job_reqs]
            
            if not job_reqs:
                continue
            
            matched = [s for s in skill_list if s in job_reqs_lower]
            missing = [r for r in job_reqs if r.lower() not in skill_list]
            match_pct = round(len(matched) / len(job_reqs) * 100) if job_reqs else 0
            
            results.append({
                'job': job,
                'match_pct': match_pct,
                'matched': matched,
                'missing': missing,
                'matched_count': len(matched),
                'total_count': len(job_reqs)
            })
        
        results.sort(key=lambda x: x['match_pct'], reverse=True)
    
    return render_template('job_match.html', results=results, user_skills=user_skills)

# ── API endpoints ─────────────────────────────────────────────────────────────

@app.route('/api/stats')
def api_stats():
    stats = db.get_dashboard_stats()
    return jsonify({'total_applications': stats['total_applications'],
                    'total_companies': stats['total_companies']})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)